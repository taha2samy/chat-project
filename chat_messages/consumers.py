import json
import logging
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from users.views.profile_views import get_all_friends
from asgiref.sync import sync_to_async
from users.models import GroupMembership
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication

logger = logging.getLogger("chat_messages")

# Get groups a user belongs to
def get_all_group(user):
    group_memberships = GroupMembership.objects.filter(user=user)
    return [i.group.id for i in group_memberships]   

class MessageConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.user = self.scope.get('user')
        logger.info(self.user)
        self.refresh = (lambda x: x.decode('utf-8') if x else None)(dict(self.scope.get('headers')).get(b'refresh'))
        try:
            refresh = await sync_to_async(RefreshToken)(self.refresh)
            id = refresh.payload.get("user_id")
        except:
            id=None
        if not self.user.is_authenticated: 
            logger.warning("Unauthenticated user attempted to connect.")
            await self.close(code=4001, reason="Unauthorized access")
            return 
        if str(self.user.id)!=str(id):
            logger.warning("Unauthenticated user attempted to connect with out refresh key")
            await self.close(code=4001, reason="Unauthorized access")
            return 

        logger.info(f"Authenticated user connected: {self.user}")
        await self.accept()
        # Start background task to fetch data and add channels
        asyncio.create_task(self._fetch_and_add_channels_to_group())

    async def _fetch_and_add_channels_to_group(self):
        # Run database queries concurrently using asyncio.gather
        all_data1, all_data2 = await asyncio.gather(
            database_sync_to_async(get_all_friends)(self.user, ['id']),
            database_sync_to_async(get_all_group)(user=self.user.id)
        )

        # Process the fetched data
        all_group_memberships = {str(i) for i in all_data2}
        all_friends_channels = {str(i['id']) for i in all_data1}
        
        self.all_channels_subscribe = all_friends_channels.union(all_group_memberships)
        del all_data1, all_data2
        for channel in self.all_channels_subscribe:
            await self.channel_layer.group_add(channel, self.channel_name)
        await self.channel_layer.group_add(str(self.user.id), self.channel_name)
    async def disconnect(self, close_code):
        logger.info(f"Connection closed with code: {close_code}")
        if hasattr(self, 'all_channels_subscribe'):
            # Remove all channels concurrently without waiting
            for channel in self.all_channels_subscribe:
                await self.channel_layer.group_discard(channel, self.channel_name)
            await self.channel_layer.group_discard(str(self.user.id), self.channel_name)
    async def receive(self, text_data):
        logger.info(f"Received message: from {self.user} {text_data}")
        try:
            message = json.loads(text_data)
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON.")
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
            return
        
        message_payload = message.get('message')
        channel_name = message.get('channel')
    
        if not channel_name or channel_name not in self.all_channels_subscribe:
            # Handle cases where no group is specified
            await self.send(text_data=json.dumps({
                'error': 'No group specified'
            }))
            return
        
        # Send the message asynchronously to the group
        await self.channel_layer.group_send(
            channel_name,
            {
                'type': 'chat_message',
                'message': message_payload,
                'from': self.user.username,
                "to": channel_name
            }
        )

    async def chat_message(self, event):
        # Send the message to the WebSocket client asynchronously
        await self.send(text_data=json.dumps(event))

    async def check_refresh_disconnect(self,event):
        if str(event["refresh"])==self.refresh:
            logger.debug("unathorized conection close from websocket")
            await self.close(code=4001, reason="Unauthorized access")