from django.urls import path
from .views.auth_views import SignUpView, LoginView, LogoutView,TokenRefreshView
from .views.profile_views import UserProfileView
from .views.user_search import UserListView
from .views.firendship import FriendshipAPIView
app_name = 'users'

urlpatterns = [
    path("users/",UserListView.as_view(),name="search"),
    path('login/', LoginView.as_view(), name='login'),  
    path('profile/', UserProfileView.as_view(), name='profile'),
    path("signup/",SignUpView.as_view(), name="signup"),
    path("logout/",LogoutView.as_view(), name="logout"),
    path('refresh-token/', TokenRefreshView.as_view(), name='refresh_token'),
    path('friendship/', FriendshipAPIView.as_view(), name='friendship'),  
  
]    