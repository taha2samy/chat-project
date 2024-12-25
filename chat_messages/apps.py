from django.apps import AppConfig


class ChatMessagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat_messages'
    def ready(self):
        import chat_messages.signals
        return super().ready()
