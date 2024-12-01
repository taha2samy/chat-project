from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework import status
from .serializers import UserSerializer,SignUpSerializer,FriendshipSerializer, GroupMembershipSerializer
from .models import GroupMembership, Friendship
from django.db.models import F
from django.conf import settings
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import get_user_model
User = get_user_model()

# logout View
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the refresh token from the request
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Decode and blacklist the refresh token
            refresh = RefreshToken(refresh_token)
            refresh.blacklist()

            return Response(
                {"message": "Successfully logged out"},
                status=status.HTTP_200_OK
            )

        except InvalidToken:
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except TokenError:
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

# SignUp View
class SignUpView(APIView):
    def post(self, request):
        # Get the data from the request
        serializer = SignUpSerializer(data=request.data)

        # Validate and create the user
        if serializer.is_valid():
            user = serializer.save()

            # Generate JWT tokens for the created user
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)

        # Return validation errors if the serializer is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Login View
class LoginView(APIView):
    def post(self, request):
        # Check if username and password are provided in the request
        username = request.data.get("username")
        password = request.data.get("password")
        
        if not username or not password:
            # Return error if either username or password is missing
            return Response(
                {"error": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Authenticate the user with the provided credentials
        user = authenticate(username=username, password=password)
        
        if user:
            # Generate JWT tokens for the authenticated user
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        
        # Return an error if authentication fails
        return Response(
            {"error": "Invalid Credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )



# Refresh token
class TokenRefreshView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Validate and decode the refresh token
            

            # Extract user_id from the refresh token
          
            refresh = RefreshToken(refresh_token)
            user_id = refresh.payload.get("user_id")
            print("1111111111111111111111111111111111")
     


            if not user_id:
                return Response(
                    {"error": "Invalid refresh token"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Retrieve the user object using user_id
            user = User.objects.get(id=user_id)

            # If ROTATE_REFRESH_TOKENS is True, generate a new refresh token
            if settings.SIMPLE_JWT['ROTATE_REFRESH_TOKENS']:
                # Blacklist the old refresh token if BLACKLIST_AFTER_ROTATION is True
                if settings.SIMPLE_JWT['BLACKLIST_AFTER_ROTATION']:
                    refresh.blacklist()

                # Create a new refresh token and access token
                new_refresh = RefreshToken.for_user(user)
                new_access_token = new_refresh.access_token
                new_refresh.set_exp(lifetime=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'])
                new_access_token.set_exp(lifetime=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'])

                return Response({
                    "access": str(new_access_token),
                    "refresh": str(new_refresh)
                })

            else:
                # If ROTATE_REFRESH_TOKENS is False, just refresh the access token
                
                access_token = refresh.access_token
                access_token.set_exp(lifetime=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'])
                return Response({
                    "access": str(access_token),
                })

        except InvalidToken:
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except TokenError:
                      return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
# User Profile View
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Serialize the user profile
        user_serializer = UserSerializer(
            user,
            exclude_fields=["user_permissions", "groups", 'password', "is_superuser", "is_staff", "is_active"]
        )

        # Fetch and serialize all groups the user is a member of
        group_memberships = GroupMembership.objects.filter(user=user)
        group_membership_serializer = GroupMembershipSerializer(group_memberships, many=True)

        # Fetch all friendships involving the user
        friendships = Friendship.objects.filter(from_user=user) | Friendship.objects.filter(to_user=user)
        friendships = friendships.exclude(status="rejected")

        # Adjust friendships to include only the "friend" field
        processed_friends = []
        for friendship in friendships:
            if friendship.from_user == user:
                processed_friends.append({'friend': friendship.to_user})
            else:
                processed_friends.append({'friend': friendship.from_user})

        # Serialize the processed friendships
        friendship_serializer = FriendshipSerializer(processed_friends, many=True)

        # Return the user's profile with groups and friendships
        return Response({
            'user_profile': user_serializer.data,
            'groups': group_membership_serializer.data,
            'friendships': friendship_serializer.data,
        })
