from django.db import models
from django.contrib.auth.models import AbstractUser
import os


def image_path(instance, filename, folder_name):
    """
    Generates a dynamic file path for the uploaded image based on the provided folder name.
    The file will be uploaded to MEDIA_ROOT/<folder_name>/<username>_<filename>.
    """
    ext = filename.split('.')[-1]  # Get the file extension
    filename = f"{instance.__class__.__name__}_{instance.id}.{ext}"  # Use the model class name and instance ID for the filename
    return os.path.join(folder_name, filename)  # Return the dynamic path


class User(AbstractUser):
    personal_image = models.ImageField(upload_to=image_path, blank=True, null=True)

    def __str__(self):
        return self.username


class Friendship(models.Model):
    from_user = models.ForeignKey(User, related_name='friendship_from', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friendship_to', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10, 
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], 
        default='pending'
    )

    class Meta:
        unique_together = ('from_user', 'to_user')  # Ensure the combination is unique
        verbose_name = 'Friendship'
        verbose_name_plural = 'Friendships'

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username} ({self.status})"


class ChatGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    group_image = models.ImageField(upload_to=image_path, blank=True, null=True)

    def __str__(self):
        return self.name


class GroupMembership(models.Model):
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
