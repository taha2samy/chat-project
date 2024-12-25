from rest_framework import serializers
from .models import Message, MessageStatus



class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = "__all__"
class MessageStatusSerializer(serializers.ModelSerializer):
    message=MessageSerializer()
    class Meta:
        model = MessageStatus
        fields = '__all__' 