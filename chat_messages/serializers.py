from rest_framework import serializers
from .models import Message, MessageStatus, ChatMessage, ChatMessageStatus,Media


class chatMessageStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessageStatus
        fields = "__all__"
class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = "__all__"

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id', 'file', 'uploaded_at']

class MessageSerializer(serializers.ModelSerializer):
    media = MediaSerializer(many=True, read_only=True)  
    media_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    ) 

    class Meta:
        model = Message
        fields = "__all__"

class MessageStatusSerializer(serializers.ModelSerializer):
    message=MessageSerializer()
    class Meta:
        model = MessageStatus
        fields = '__all__'


