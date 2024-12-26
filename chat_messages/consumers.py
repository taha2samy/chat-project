import json
import uuid
import logging
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async

from rest_framework_simplejwt.tokens import RefreshToken
from .models import Message,MessageStatus,ChatMessage,ChatMessageStatus
from .serializers import MessageStatusSerializer
from users.serializers import FriendshipSerializer
from .database_async import get_all_group,get_all_friendship
from .encoder import CustomJSONEncoder
logger = logging.getLogger("chat_messages")


class MessageConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_frindshipserializer(self,data):
        l=FriendshipSerializer(data)
        return l.data

    async def connect(self):
        self.user = self.scope.get('user')
        self.refresh = self._get_refresh_token_from_headers()
        
        # Authenticate user
        if not await self._authenticate_user():
            return

        logger.info(f"Authenticated user connected: {self.user}")
        await self.accept()

        # Start background task to fetch data and add channels
        asyncio.create_task(self._fetch_and_add_channels_to_group())

    def _get_refresh_token_from_headers(self):
        """Extract the refresh token from WebSocket headers."""
        return (lambda x: x.decode('utf-8') if x else None)(dict(self.scope.get('headers')).get(b'refresh'))

    async def _authenticate_user(self):
        """Authenticate the user by verifying the refresh token."""
        # Check if user is authenticated
        if not self.user.is_authenticated:
            logger.warning("Unauthenticated user attempted to connect.")
            await self.close(code=4001, reason="Unauthorized access")
            return False

        # Check if user ID matches the refresh token
        user_id_from_refresh = await self._get_user_id_from_refresh_token(self.refresh)
        if str(self.user.id) != str(user_id_from_refresh):
            logger.warning("User ID mismatch with refresh token.")
            await self.close(code=4001, reason="Unauthorized access")
            return False

        return True

    @sync_to_async
    def _get_user_id_from_refresh_token(self, refresh_token):
        """Retrieve user ID from the refresh token payload."""
        try:
            refresh = RefreshToken(refresh_token)
            return refresh.payload.get("user_id")
        except Exception as e:
            logger.error(f"Error decoding refresh token: {e}")
            return None

    async def _fetch_and_add_channels_to_group(self):
        all_friendships = await get_all_friendship(self.user)
        all_groups = await get_all_group(self.user)
        self.all_friends=[]
        for i in all_friendships:
            if self.user.id==i.from_user_id:
                self.all_friends.append({"id":i.id,"friend":i.to_user_id})
            else:
                self.all_friends.append({"id":i.id,"friend":i.from_user_id})
        all_group_memberships = {str(i.id) for i in all_friendships}
        all_friends_channels = {str(i["id"]) for i in all_groups}

        self.all_channels_subscribe = all_friends_channels.union(all_group_memberships)
        for channel in self.all_channels_subscribe:
            logger.debug(f"consumer {self.user.username}  subscribe {channel}")
            await self.channel_layer.group_add(channel, self.channel_name)
            
        pass
        await self.channel_layer.group_add(str(self.user.id), self.channel_name)
    async def disconnect(self, close_code):
        logger.info(f"Connection closed with code: {close_code}")
        if hasattr(self, 'all_channels_subscribe'):
            # Remove all channels concurrently without waiting
            for channel in self.all_channels_subscribe:
                await self.channel_layer.group_discard(channel, self.channel_name)
            await self.channel_layer.group_discard(str(self.user.id), self.channel_name)
    
    async def handler_friendship(self,event):
        msg = await self.get_frindshipserializer(event["friendship"])
        await self.send(text_data=json.dumps({"friendship": msg,"type":"frienship_message"}, cls=CustomJSONEncoder))  # Use the custom encoder here
        pass

        pass

    async def receive(self, text_data):
        logger.info(f"Received message: from {self.user}")
        try:
            message = json.loads(text_data)
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON.")
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
            return
        message_type =message.get("type",None)

        if message_type=="friendship_notification_seen":
            try:
                message_channel=message.get("channel")
                message_id=message.get("message_id")
                message_status=  await database_sync_to_async(MessageStatus.objects.get)(message__id=str(message_id),message__receiver__id=self.user.id)
                message_status.is_seen=True
                await database_sync_to_async(message_status.save)()
            except:
                await self.send(json.dumps({"error":"this message id is not exist or channel"}))
            pass

        if message_type=="friendship_message":
            message_payload= message.get("content",None)
            message_media=message.get("media",None)
            message_channel=message.get("channel")
            if message_media != None:
                pass
            friend = None
            for channel in self.all_friends:
                channel_friend = str(channel.get("id"))
                if channel_friend == message_channel:
                    friend = channel.get("friend")
                    break
            if friend == None:
                return
            message = await database_sync_to_async(Message.objects.create)(friendship_id=message_channel,
                                    sender=self.user,
                                    content=message_payload
                                    )
            message_status = await database_sync_to_async(MessageStatus.objects.create)(message=message,receiver_id=friend)

        if message_type=="group_message":
            message_payload= message.get("content",None)
            message_media=message.get("media",None)
            message_channel=message.get("channel")
            if message_media != None:
                pass
            
            message = await database_sync_to_async(ChatMessage.objects.create)(chatgroup_id=message_channel,
                                                               sender=self.user,
                                                               content=message_payload)
            
            pass
            
            

    async def send_notification_chatgroup(self,event):
        if self.user.id != event["chat_message_status"]["receiver"]:
            await self.send(text_data=json.dumps({"message":event["chat_message_status"],"type":"chat_message_notification"}, cls=CustomJSONEncoder))    
        pass
    async def message_group(self, event):
        if self.user.id == event["chat_message"]["sender"]:
            pass

        else:
            await database_sync_to_async(ChatMessageStatus.objects.create)(message_id=event["chat_message"]["id"],receiver_id=self.user.id,is_received=True)            

            pass
        await self.send(text_data=json.dumps({"type":"group_message","message":event["chat_message"]},cls=CustomJSONEncoder))

    async def message_friendship(self,event):
        await self.send(text_data=json.dumps({"type":"friendship_message","message":event["chat_message"]},cls=CustomJSONEncoder))
        if self.user.id != event["chat_message"]["sender"]:
            msg=await database_sync_to_async(MessageStatus.objects.get)(message_id=event["chat_message"]["id"])
            msg.is_received=True
            await database_sync_to_async(msg.save)()
        pass
    async def check_refresh_disconnect(self,event):
        if str(event["refresh"])==self.refresh:
            logger.debug("unathorfetchedized conection close from websocket")
            await self.close(code=4001, reason="Unauthorized access")
    async def send_notification_friendship (self,event):
        if self.user.id!=event["message"]["receiver"]:
            await self.send(text_data=json.dumps({"message":event["message"],"type":"chat_friendship_notification"}, cls=CustomJSONEncoder))
        pass

    async def add_remove_friendship(self,event):
        if event['accepted']:
            self.all_friends.append({"id": event["friendship"], "friend": event["from_user_id"] if self.user.id == event["to_user_id"] else event["to_user_id"]})
            self.all_channels_subscribe.add(str(str(event["friendship"])))
            await self.channel_layer.group_add(str(event["friendship"]), self.channel_name)
            logger.debug(f"consumer {self.user.username}  subscribe {event["friendship"]}")
        else:
            try:
                self.all_friends.remove({"id": event["friendship"], "friend": event["from_user_id"] if self.user.id == event["to_user_id"] else event["to_user_id"]})
                self.all_channels_subscribe.discard(str(event["friendship"]))
                await self.channel_layer.group_discard(str(event["friendship"]), self.channel_name)
                logger.debug(f"consumer {self.user.username}  unsubscribe {event["friendship"]}")
            except:
                pass
        pass