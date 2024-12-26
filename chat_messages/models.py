from django.db import models
from users.models import Friendship,ChatGroup,User
from django.contrib.auth import get_user_model
import uuid
import logging
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

User = get_user_model()

logger = logging.getLogger("chat_messages")

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
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    media = models.ManyToManyField(Media, related_name='messages', blank=True)
    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"

class MessageStatus(models.Model):
    message = models.OneToOneField(Message, related_name='statuses', on_delete=models.CASCADE,primary_key=True)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    is_seen = models.BooleanField(default=False)
    is_received = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Status of message {self.message}"


class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, related_name='sent_messages_chat', on_delete=models.CASCADE)
    chatgroup=models.ForeignKey(ChatGroup,on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    media = models.ManyToManyField(Media, related_name='chat_messages', blank=True)
    def __str__(self):
         return f"Message from {self.sender.username} "

class ChatMessageStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message=models.ForeignKey(ChatMessage,on_delete=models.CASCADE)
    receiver=models.ForeignKey(User,on_delete=models.CASCADE)
    is_seen = models.BooleanField(default=False)
    is_received = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now_add=True)
    pass

