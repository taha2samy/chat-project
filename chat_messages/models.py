from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

logger = logging.getLogger("chat_messages")

@receiver(post_save, sender=BlacklistedToken)
def on_blacklisted_token_created(sender, instance, created, **kwargs):
    if created:
        channel_name=f"{instance.token.user_id}"
