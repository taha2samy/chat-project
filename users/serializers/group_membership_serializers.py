from rest_framework import serializers
from users.models import GroupMembership
from users.serializers.user_serializers import UserSerializer

# Group Membership Serializer
class GroupMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(exclude_fields=["date_joined", "password", "user_permissions", "groups", "is_superuser", "is_staff", "is_active"])
    group = serializers.CharField(source='group.name')

    class Meta:
        model = GroupMembership
        fields = ['user', 'group', 'role', 'date_joined']
