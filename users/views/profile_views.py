from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer
from rest_framework import  status

import logging
# Set up logging
logger = logging.getLogger("users")

User=get_user_model()

# User Profile View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from users.serializers import UserSerializer

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request):
        """
        Get the profile of the currently authenticated user.
        """
        user = request.user
        # Exclude fields you don't want to show
        serializer = UserSerializer(User.objects.get(id=user.id), exclude_fields=['is_staff', 'is_active', 'date_joined', 'groups', 'user_permissions'])
        return Response(serializer.data)

    def patch(self, request):
        """
        Update the profile of the currently authenticated user.
        """
        user = request.user
        # Pass the request data to the serializer
        serializer = UserSerializer(User.objects.get(id=user.id), data=request.data, partial=True)
        logger.warning(f"{request.data}")
        # Validate the data
        try:
            if serializer.is_valid():

                # Save the updated data
                serializer.save()

                # Return the updated data in the response
                return Response(serializer.data)
        except:
            pass

        # Return any validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
