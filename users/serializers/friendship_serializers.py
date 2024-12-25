from rest_framework import serializers
from users.models import Friendship
from users.serializers.user_serializers import UserSerializer

# Friendship Serializer
class FriendshipSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(exclude_fields=["date_joined", "last_login", "user_permissions", "groups", 'password', "is_superuser", "is_staff", "is_active"])
    to_user= UserSerializer(exclude_fields=["date_joined", "last_login", "user_permissions", "groups", 'password', "is_superuser", "is_staff", "is_active"])
    class Meta:
        model = Friendship
        fields = "__all__"
    def validate(self, attrs):
        from_user = self.context['request'].user
        to_user = attrs.get('to_user')

        if from_user == to_user:
            raise serializers.ValidationError("You cannot create a friendship with yourself.")
        
        # Check if a friendship already exists between these users
        if Friendship.objects.filter(from_user=from_user, to_user=to_user).exists() or \
           Friendship.objects.filter(from_user=to_user, to_user=from_user).exists():
            raise serializers.ValidationError("A friendship request between these users already exists.")
        
        return attrs
    def create(self, validated_data):
        validated_data['from_user'] = self.context['request'].user
        return super().create(validated_data)
