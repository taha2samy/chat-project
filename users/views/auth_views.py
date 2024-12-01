from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework import status
from users.serializers import SignUpSerializer
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import get_user_model
from django.conf import settings
import logging
logger = logging.getLogger("users")

User = get_user_model()

# Logout View
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            logger.error("Logout attempt failed: Missing refresh token.")
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh = RefreshToken(refresh_token)
            refresh.blacklist()
            logger.info(f"User {request.user.username} logged out successfully.")
            return Response(
                {"message": "Successfully logged out"},
                status=status.HTTP_200_OK
            )

        except InvalidToken:
            logger.warning(f"Invalid or expired refresh token used by {request.user.username}.")
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except TokenError:
            logger.error("Token error occurred during logout attempt.")
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

# SignUp View
class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            logger.info(f"New user {user.username} registered successfully.")
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)

        logger.warning("Sign-up failed: Invalid data provided.")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Login View
class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            logger.warning("Login attempt failed: Username or password missing.")
            return Response(
                {"error": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            logger.info(f"User {username} logged in successfully.")
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })

        logger.warning(f"Invalid login attempt: Incorrect credentials for {username}.")
        return Response(
            {"error": "Invalid Credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )


# Refresh Token View
class TokenRefreshView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            logger.warning("Token refresh attempt failed: Missing refresh token.")
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh = RefreshToken(refresh_token)
            user_id = refresh.payload.get("user_id")

            if not user_id:
                logger.warning("Token refresh failed: Missing user_id in refresh token.")
                return Response(
                    {"error": "Invalid refresh token"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            user = User.objects.get(id=user_id)

            if settings.SIMPLE_JWT['ROTATE_REFRESH_TOKENS']:
                if settings.SIMPLE_JWT['BLACKLIST_AFTER_ROTATION']:
                    refresh.blacklist()
                    logger.info(f"Refresh token blacklisted for user {user.username}.")

                new_refresh = RefreshToken.for_user(user)
                new_access_token = new_refresh.access_token
                new_refresh.set_exp(lifetime=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'])
                new_access_token.set_exp(lifetime=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'])

                logger.info(f"Token refresh successful for user {user.username}.")
                return Response({
                    "access": str(new_access_token),
                    "refresh": str(new_refresh)
                })

            else:
                access_token = refresh.access_token
                access_token.set_exp(lifetime=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'])
                logger.info(f"Access token refreshed for user {user.username}.")
                return Response({
                    "access": str(access_token),
                })

        except InvalidToken:
            logger.error(f"Invalid or expired refresh token used for user {request.user.username}.")
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except TokenError:
            logger.error("Token error occurred during token refresh.")
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
