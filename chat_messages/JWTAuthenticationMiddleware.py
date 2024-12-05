import jwt
from channels.auth import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.models import TokenUser
from channels.db import database_sync_to_async

User = get_user_model()  # Replace with your custom user model if applicable


class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom WebSocket middleware to handle JWT authentication in a stateless manner.
    """

    async def __call__(self, scope, receive, send):
        # Get the JWT token from the WebSocket headers
        token = None
        try:
            for key, value in scope["headers"]:
                if key == b"authorization":
                    token = value.decode().split(" ")[1]  # 'Bearer <token>'
            
            if token:
                try:
                    # Validate the JWT token and extract user information
                    user = await self.authenticate_token(token)
                    scope["sss"]=token
                    scope["user"] = user
                except InvalidToken:
                    scope["user"] = AnonymousUser()
            else:
                scope["user"] = AnonymousUser()
        except Exception as e:
            scope["access_token"] = token
            scope["user"] = AnonymousUser()
        return await super().__call__(scope, receive, send)

    async def authenticate_token(self, token):
        """
        Authenticate the token and return a user instance if it exists, otherwise return a TokenUser.
        """
        try:
            # Decode and verify the token using JWTStatelessUserAuthentication
            jwt_auth = JWTStatelessUserAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            
            # Extract the user_id claim
            user_id = validated_token.get("user_id")
            if user_id:
                # Check if a user with this ID exists in the database
                user = await self.get_user_from_database(user_id)
                if user:
                    return user
            
            # If no user in the database, return the stateless TokenUser
            return jwt_auth.get_user(validated_token)  # Returns a TokenUser
        except Exception as e:
            raise InvalidToken(f"Invalid token: {str(e)}")

    @database_sync_to_async
    def get_user_from_database(self, user_id):
        """
        Retrieve the user instance from the database.
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
