import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# Set up logging
logger = logging.getLogger("users")
User=get_user_model()
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated
    excluded_fields_from_update = ['id',"last_login", 'is_staff', 'is_active', 'groups', 'user_permissions', 'is_superuser']
    excluded_fields_from_response = excluded_fields_from_update.remove("id")
    def get(self, request):
        """
        Get the profile of the currently authenticated user.
        """
        user = request.user
        # Exclude fields you don't want to show
        serializer = UserSerializer(User.objects.get(id=user.id), exclude_fields=UserProfileView.excluded_fields_from_update)
        return Response(serializer.data)

    def patch(self, request):
        """
        Update the profile of the currently authenticated user.
        """
        user = request.user

        # Get the user data and exclude fields that should not be updated
        data = request.data.copy()
        

    # Remove the excluded fields from the request data
        for field in UserProfileView.excluded_fields_from_update:
            data.pop(field, None)

        # Pass the filtered request data to the serializer
        serializer = UserSerializer(User.objects.get(id=user.id,), data=data, partial=True)


        # Validate the data
        try:
            if serializer.is_valid():
                # Check if password is being updated
                new_password = data.get('password')
                if new_password:
                    try:
                        # Validate the password
                        validate_password(new_password, user=user)
                    except ValidationError as e:
                        # Return password validation errors
                        return Response({'password': e.messages}, status=status.HTTP_400_BAD_REQUEST)
                
                # Save the updated data
                serializer.save()

                # Return the updated data in the response
                response_data = serializer.data
                for field in UserProfileView.excluded_fields_from_response:
                    response_data.pop(field, None)
                
                return Response(response_data)
        except Exception as e:
            logger.error(f"Error updating profile: {e}")

        # Return any validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
