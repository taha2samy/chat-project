from rest_framework import serializers
from users.models import Friendship
from users.serializers.user_serializers import UserSerializer

# Friendship Serializer
class FriendshipSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(exclude_fields=["date_joined", "last_login", "user_permissions", "groups", 'password', "is_superuser", "is_staff", "is_active"])
    to_user= UserSerializer(exclude_fields=["date_joined", "last_login", "user_permissions", "groups", 'password', "is_superuser", "is_staff", "is_active"])
    class Meta:
        model = Friendship
        fields = ["id",'from_user',"to_user", 'status_to_user','status_from_user', 'date_created']
