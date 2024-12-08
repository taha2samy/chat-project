from rest_framework import serializers
from .models import Message, MessageStatus

class MessageStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageStatus
        fields = '__all__' 

class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ['id', 'friendship', 'sender', 'receiver', 'content', 'created_at', 'media', ]
