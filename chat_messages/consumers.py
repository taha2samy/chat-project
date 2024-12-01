import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging
logger = logging.getLogger("chat_messages")

class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        logger.info(user)
        if not user.is_authenticated:
            logger.warning("Unauthenticated user attempted to connect.")
            await self.close(code=4001, reason="Unauthorized access")

            return 
        logger.info(f"Authenticated user connected: {user}")
        await self.accept()
        # Sending a test message in a loop (example only; might be removed in production)
        for _ in range(1000):
            await self.send("hiiiiiiiiiiiiii")

    async def disconnect(self, close_code):
        logger.info(f"Connection closed with code: {close_code}")

    async def receive(self, text_data):
        logger.info(f"Received message: {text_data}")
        logger.warning("Test warning message.")
