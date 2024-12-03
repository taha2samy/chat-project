import jwt
from channels.auth import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from channels.db import database_sync_to_async
import json

class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom WebSocket middleware to handle JWT authentication.
    """

    async def __call__(self, scope, receive, send):
        # Get the JWT token from the WebSocket headers
        token = None
        try:

            for key, value in scope['headers']:
                if key == b'authorization':
                    token = value.decode().split(' ')[1]  # 'Bearer <token>'

            if token:
                try:
                    # Validate the JWT token and extract user information
                    user = await self.authenticate_token(token)
                    scope['user'] = user
                except:
                    scope['user'] = AnonymousUser()
            else:
                scope['user'] = AnonymousUser()
            
           
        except:
            scope["access_token"]=token
            scope["user"]=AnonymousUser()
        return await super().__call__(scope, receive, send)
    @database_sync_to_async
    def authenticate_token(self, token):
        """
        Authenticate the token and return the associated user.
        """
        try:
            # Decode and verify the token using JWTAuthentication from rest_framework_simplejwt
            validated_token = JWTAuthentication().get_validated_token(token)
            user = JWTAuthentication().get_user(validated_token)
            return user
        except Exception as e:
            raise jwt.InvalidTokenError(f"Invalid token: {str(e)}")

