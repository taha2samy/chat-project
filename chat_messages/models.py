from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

import logging
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

logger = logging.getLogger("chat_messages")

@receiver(post_save, sender=BlacklistedToken)
def on_blacklisted_token_created(sender, instance, created, **kwargs):
    if created:
        channel_name = f"{instance.token.user_id}"  # Assuming you use the user's ID in the channel name
        channel_layer = get_channel_layer()

        # Send a disconnect message to the WebSocket handler
        async_to_sync(channel_layer.group_send)(
            channel_name,  # Channel name should match the user's WebSocket channel
            {
                "type": "check_refresh_disconnect",
                "refresh":instance.token.token  
            }
        )
