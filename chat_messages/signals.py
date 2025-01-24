from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from chat_messages.models import MessageStatus,ChatMessage,ChatMessageStatus,Message
from .serializers import ChatMessageSerializer,chatMessageStatusSerializer,MessageSerializer,MessageStatusSerializer
import logging

logger = logging.getLogger("chat_messages")

@receiver(post_save, sender=MessageStatus)
def send_group_notification(sender, instance, created, **kwargs):
   
    if created:
        channel_layer = get_channel_layer()
        try:
            # Serialize the MessageStatus instance
            serializer = MessageStatusSerializer(instance)
            serialized_data = serializer.data
            # Send serialized data to the group
            async_to_sync(channel_layer.group_send)(str(instance.message.friendship.id),
                {
                    'type': 'message_friendship',
                    "chat_message": serialized_data,  # Pass serialized data
                }
            )
            logger.info(f"Message status {instance.message.id} sent in friendship {instance.message.friendship.id}")
        except Exception as e:
            logger.error(f"Failed to send notification for message status {instance.message.id}: {e}")

            

    if instance.is_received or instance.is_seen:
        channel_layer = get_channel_layer()
        serializer=MessageStatusSerializer(instance)
        serialized_data=serializer.data

        try:
            async_to_sync(channel_layer.group_send)(
                str(instance.message.friendship.id),
                {
                    'type': 'send_notification_friendship',
                    "message": serialized_data,
                }
            )
            logger.info(f"Notification sent for message {instance.message.id} in friendship {instance.message.friendship.id}")
        except Exception as e:
            logger.error(f"Failed to send notification for message {instance.message.id}: {e}")


@receiver(post_save, sender=ChatMessageStatus)
def send_notification(sender, instance, created, **kwargs):
    
    if instance.is_received or instance.is_seen:
        channel_layer = get_channel_layer()
        serializer=chatMessageStatusSerializer(instance)
        serialized_data=serializer.data
        try:
            async_to_sync(channel_layer.group_send)(
                str(instance.message.chatgroup.id),
                {
                    'type': 'send_notification_chatgroup',
                    "chat_message_status": serialized_data,
                }
            )
            logger.info(f"Notification sent for chat message {instance.message.id} in chat group {instance.message.chatgroup.id}")
        except Exception as e:
            logger.error(f"Failed to send notification for chat message {instance.message.id}: {e}")

@receiver(post_save, sender=ChatMessage)
def send_group_notification(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    if created:
        try:
            # Serialize the ChatMessage instance
            serializer = ChatMessageSerializer(instance)
            serialized_data = serializer.data
            
            # Send serialized data to the group
            async_to_sync(channel_layer.group_send)(
                str(instance.chatgroup.id),
                {
                    'type': 'message_group',
                    "chat_message": serialized_data,  # Pass serialized data
                }
            )
            logger.info(f"Message {instance.id} sent in chat group {instance.chatgroup.id}")
        except Exception as e:
            logger.error(f"Failed to send notification for chat message {instance.id}: {e}")
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


