from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import logging
import uuid
import os
logger = logging.getLogger("chat_messages")


def image_path(instance, filename):
    """
    Generates a dynamic file path for the uploaded image based on the instance's ID.
    The file will be uploaded to MEDIA_ROOT/<folder_name>/<instance_id>_<filename>.
    """
    folder_name = "user_images"  # Specify the folder name dynamically or statically
    ext = filename.split('.')[-1]  # Get the file extension
    filename = f"{instance.__class__.__name__}_{instance.id}.{ext}"  # Use the model class name and instance ID for the filename
    return os.path.join(folder_name, filename)  # Return the dynamic path


def generate_uuid_for_user():
    return uuid.uuid5(uuid.NAMESPACE_DNS, "Users"+str(uuid.uuid4()))


def generate_uuid_for_friendship():
    return uuid.uuid5(uuid.NAMESPACE_DNS, "Friendship"+str(uuid.uuid4()))


def generate_uuid_for_chatgroup():
    return uuid.uuid5(uuid.NAMESPACE_DNS, "chatgroup"+str(uuid.uuid4()))


def generate_uuid_for_group_membership():
    return uuid.uuid5(uuid.NAMESPACE_DNS, "GroupMembership"+str(uuid.uuid4()))


class User(AbstractUser):
    id = models.UUIDField(default=generate_uuid_for_user, editable=False, primary_key=True)
    personal_image = models.ImageField(upload_to=image_path, blank=True, null=True)

    def __str__(self):
        return self.username


class Friendship(models.Model):
    id = models.UUIDField(default=generate_uuid_for_friendship, editable=False, primary_key=True)
    from_user = models.ForeignKey(User, related_name='friendship_from', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friendship_to', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    status_from_user = models.CharField(
        max_length=10, 
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], 
        default='pending'
    )
    status_to_user = models.CharField(
        max_length=10, 
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], 
        default='pending'
    )

    class Meta:
        unique_together = ('from_user', 'to_user')  # Ensure the combination is unique
        verbose_name = 'Friendship'
        verbose_name_plural = 'Friendships'

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username}"


class ChatGroup(models.Model):
    id = models.UUIDField(default=generate_uuid_for_chatgroup, editable=False, primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    group_image = models.ImageField(upload_to=image_path, blank=True, null=True)

    def __str__(self):
        return self.name


class GroupMembership(models.Model):
    id = models.UUIDField(default=generate_uuid_for_group_membership, editable=False, primary_key=True)
    MEMBER = 'member'
    ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (MEMBER, 'Member'),
        (ADMIN, 'Admin')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=MEMBER)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'group')  # Prevent multiple memberships in the same group

    def __str__(self):
        return f"{self.user.username} - {self.group.name} ({self.role})"

@receiver(post_save,sender=Friendship)
def add_or_remove_friendship(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    for channel in [instance.from_user_id,instance.to_user_id]:
        async_to_sync(channel_layer.group_send)(
            str(channel), 
            {
                "type": "add_remove_friendship",
                "friendship":instance.id,
                "accepted":False if instance.status_to_user=="rejected" or instance.status_from_user=="rejected" else True,
                "from_user_id":instance.from_user_id,
                "to_user_id":instance.to_user_id

            }
            
        )
        async_to_sync(channel_layer.group_send)(
            str(channel), 
            {
                "type": "handler_friendship",
                "friendship":instance,

            }
            
        )
    
    