from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from users.models import Friendship
from django.contrib.auth import get_user_model
import uuid
import logging
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

User = get_user_model()

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
class Media(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='media/files/', null=False)  # Media file field
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Media {self.id} uploaded at {self.uploaded_at}"


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    friendship = models.ForeignKey(Friendship, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    media = models.ManyToManyField(Media, related_name='messages', blank=True)
    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"

class MessageStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.OneToOneField(Message, related_name='statuses', on_delete=models.CASCADE)
    is_seen = models.BooleanField(default=False)
    is_received = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Status of message {self.message}"



@receiver(post_save, sender=MessageStatus)
def send_group_notification(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()

    if instance.is_received or instance.is_seen:
        try:
            async_to_sync(channel_layer.group_send)(
                str(instance.message.friendship.id),
                {
                    'type': 'send_notification_friendship',
                    "is_seen": instance.is_seen,
                    "is_received": instance.is_received,
                    'message': str(instance.id),
                    "owner": instance.message.sender.id,
                    "channel":str(instance.message.friendship.id),
                }
            )
            logger.info(f"Notification sent for message {instance.id} in friendship {instance.message.friendship.id}")
        except Exception as e:
            logger.error(f"Failed to send notification for message {instance.id}: {e}")
