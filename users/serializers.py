from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Friendship, GroupMembership, ChatGroup

User = get_user_model()

# User Serializer for Profile
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'  # Include all fields by default

    def __init__(self, *args, **kwargs):
        # Get the fields to include or exclude from kwargs
        include_fields = kwargs.pop('include_fields', None)
        exclude_fields = kwargs.pop('exclude_fields', None)
        
        # Initialize the parent class
        super().__init__(*args, **kwargs)

        # Dynamically adjust the fields
        if include_fields is not None:
            allowed = set(include_fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        
        if exclude_fields is not None:
            for field_name in exclude_fields:
                self.fields.pop(field_name, None)


# Friendship Serializer
class FriendshipSerializer(serializers.ModelSerializer):
    friend = UserSerializer(exclude_fields=["date_joined","last_login","user_permissions","groups",'password',"is_superuser","is_staff","is_active"])

    class Meta:
        model = Friendship
        fields = [ "id",'friend', 'status', 'date_created']

# Group Membership Serializer
class GroupMembershipSerializer(serializers.ModelSerializer):
    group = serializers.CharField(source='group.name')
    role = serializers.CharField()

    class Meta:
        model = GroupMembership
        fields = ['group', 'role', 'date_joined']



class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, attrs):
        # Ensure passwords match
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Passwords must match.")
        return attrs

    def create(self, validated_data):
        # Remove password2 as it is not needed in the user model
        validated_data.pop('password2')

        # Create the user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
