from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

# User Serializer for Profile
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    personal_image = serializers.ImageField(required=False)


    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        include_fields = kwargs.pop('include_fields', None)
        exclude_fields = kwargs.pop('exclude_fields', None)
        super().__init__(*args, **kwargs)

        if include_fields is not None:
            allowed = set(include_fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if exclude_fields is not None:
            for field_name in exclude_fields:
                self.fields.pop(field_name, None)
    def validate_password(self, value):
        """
        Validate password (if provided).
        """
        if value:
            validate_password(value)
        return value

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        personal_image = validated_data.pop('personal_image', None)

        # Update the instance with other data
        instance = super().update(instance, validated_data)

        # If password is provided, set the new password
        if password:
            instance.set_password(password)

        # If a personal image is provided, update it
        if personal_image:
            instance.personal_image = personal_image

        instance.save()
        return instance
