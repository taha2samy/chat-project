from django.urls import path
from .views import FriendshipMessageAPIView,FriendshipNotificationSeenView
app_name = 'chat_messages'

urlpatterns = [
    path('friendship/', FriendshipMessageAPIView.as_view()),
    path('friendship/notification/seen/', FriendshipNotificationSeenView.as_view()),  
]    