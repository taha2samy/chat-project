from rest_framework import serializers
from users.models import ChatGroup

# Chat Group Serializer
class ChatGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatGroup
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'group_image']
