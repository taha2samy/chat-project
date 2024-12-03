import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging
from users.views.profile_views import get_all_friends
from asgiref.sync import sync_to_async
from users.models import GroupMembership
from channels.db import database_sync_to_async


logger = logging.getLogger("chat_messages")

def get_all_group(user):
    group_memberships = GroupMembership.objects.filter(user=user)
    return [i.group.id for i in group_memberships]   

class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        logger.info(self.user)
        if not self.user.is_authenticated:
            logger.warning("Unauthenticated user attempted to connect.")
            await self.close(code=4001, reason="Unauthorized access")
            return 
        logger.info(f"Authenticated user connected: {self.user}")
        await self.accept()
        all_data1=await database_sync_to_async(get_all_friends)(self.user,['id'])
        all_data2 = await database_sync_to_async(get_all_group)(user=self.user)
        all_group_memberships={f"{i}-g" for i in all_data2}
        all_friends_channels = {f"{i['id']}-r" for i in all_data1}
        self.all_channels_subscribe = all_friends_channels.union(all_group_memberships)
        del all_data1,all_data2
        for channel in self.all_channels_subscribe:
            await self.channel_layer.group_add(
                channel,
                self.channel_name
            )
        logger.warning(f"\n {self.all_channels_subscribe} \n")
    async def disconnect(self, close_code):
        logger.info(f"Connection closed with code: {close_code}")
        for channel in self.all_channels_subscribe:
            await self.channel_layer.group_discard(
                channel,
                self.channel_name
            )

        
    async def receive(self, text_data):
        logger.info(f"Received message: from {self.user} {text_data}")
        try:
            message = json.loads(text_data)
        except:
            logger.error(f"Failed to parse JSON:")
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))

            return
        logger.warning("hiiiiiiiiiiiiiiiiiiiiiiiiii work")
        message_payload = message.get('message')
        channel_name = message.get('channel')
    
        if not channel_name or (channel_name not in self.all_channels_subscribe):
            # Handle cases where no group is specified
            await self.send(text_data=json.dumps({
                'error': 'No group specified'
            }))
            return
        await self.channel_layer.group_send(
            channel_name,
            {
                'type': 'chat_message',
                'message': message_payload,
                'from': self.user.username,
                "to":channel_name
            }
        )
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

        
