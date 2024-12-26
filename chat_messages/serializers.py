from rest_framework import serializers
from .models import Message, MessageStatus, ChatMessage, ChatMessageStatus


class chatMessageStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessageStatus
        fields = "__all__"
class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = "__all__"


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = "__all__"
class MessageStatusSerializer(serializers.ModelSerializer):
    message=MessageSerializer()
    class Meta:
        model = MessageStatus
        fields = '__all__' 