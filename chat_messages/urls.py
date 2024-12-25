from django.urls import path
from .views import MessageStatusView
app_name = 'chat_messages'

urlpatterns = [
    path('friendship/<uuid:friendship_id>/messages/', MessageStatusView.as_view()),  
]    