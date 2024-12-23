import json
import uuid
import logging
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Message,MessageStatus
from .Serializer import MessageSerializer
from .database_async import get_all_group,get_all_friendship
from .encoder import CustomJSONEncoder
logger = logging.getLogger("chat_messages")


class MessageConsumer(AsyncWebsocketConsumer):

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
        logger.warning(f"Friendship data: {all_friendships}")
        all_groups = await get_all_group(self.user)
        self.all_friends=[{"id":i.id,"friend":self.user.id if self.user.id!=i.from_user_id else i.to_user_id} for i in all_friendships]
        logger.warning(self.all_friends)
        all_group_memberships = {str(i.id) for i in all_friendships}
        all_friends_channels = {str(i.id) for i in all_groups}

        self.all_channels_subscribe = all_friends_channels.union(all_group_memberships)
        for channel in self.all_channels_subscribe:
            logger.debug(f"consumer {channel}")
            await self.channel_layer.group_add(channel, self.channel_name)
            await self.channel_layer.group_add(str(self.user.id), self.channel_name)
        pass
    async def disconnect(self, close_code):
        logger.info(f"Connection closed with code: {close_code}")
        if hasattr(self, 'all_channels_subscribe'):
            # Remove all channels concurrently without waiting
            for channel in self.all_channels_subscribe:
                await self.channel_layer.group_discard(channel, self.channel_name)
            await self.channel_layer.group_discard(str(self.user.id), self.channel_name)
    


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

        if message_type=="friendship":
            message_payload= message.get("payload",None)
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
                                    receiver_id=str(friend),
                                    content=message_payload
                                    )
            message_status = await database_sync_to_async(MessageStatus.objects.create)(message=message)
            await database_sync_to_async(message_status.save)()
            await self.channel_layer.group_send(message_channel,{
                    "type":"frienship_message",
                    "message":message,
                    "message_status":message_status
                })
            
            

        
    async def group_message(self, event):
        pass

    async def frienship_message(self,event):
        @database_sync_to_async
        def get_receiver_of_message(message):
            return message.receiver
        @database_sync_to_async
        def get_serlizer_message(message):
            l =MessageSerializer(message)
            return l.data
        message_status=event["message_status"]
        if (await get_receiver_of_message(event["message"]))==self.user:
             message_status.is_received = True
             await database_sync_to_async(message_status.save)()
        message = await get_serlizer_message(event["message"])
        await self.send(text_data=json.dumps({"message": message}, cls=CustomJSONEncoder))  # Use the custom encoder here
        pass
    async def check_refresh_disconnect(self,event):
        if str(event["refresh"])==self.refresh:
            logger.debug("unathorfetchedized conection close from websocket")
            await self.close(code=4001, reason="Unauthorized access")
    async def send_notification_friendship (self,event):
        if str(event["owner"])==str(self.user.id):
            await self.send(text_data=json.dumps({"message": event["message"],"is_seen":event["is_seen"],"is_received":event["is_received"],"channel":event["channel"]}, cls=CustomJSONEncoder))    
            pass