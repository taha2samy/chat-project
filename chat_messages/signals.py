from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from chat_messages.models import MessageStatus
import logging

logger = logging.getLogger("chat_messages")


@receiver(post_save, sender=BlacklistedToken)
def on_blacklisted_token_created(sender, instance, created, **kwargs):
    if created:
        channel_name = f"{instance.token.user_id}"  # Assuming you use the user's ID in the channel name
        channel_layer = get_channel_layer()

        # Send a disconnect message to the WebSocket handler
        async_to_sync(channel_layer.group_send)(
            channel_name,
            {
                "type": "check_refresh_disconnect",
                "refresh": instance.token.token,
            }
        )


@receiver(post_save, sender=MessageStatus)
def send_group_notification(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()

    if instance.is_received or instance.is_seen:
        
        try:
            async_to_sync(channel_layer.group_send)(
                str(instance.message.friendship.id),
                {
                    'type': 'send_notification_friendship',
                    "message_status": instance,
                }
            )
            logger.info(f"Notification sent for message {instance.id} in friendship {instance.message.friendship.id}")
        except Exception as e:
            logger.error(f"Failed to send notification for message {instance.id}: {e}")
