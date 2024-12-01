from django.urls import path
from .views import LoginView, TokenRefreshView ,ProfileView,SignUpView,LogoutView
app_name = 'users'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),  
    path('profile/', ProfileView.as_view(), name='profile'),
    path("signup/",SignUpView.as_view(), name="signup"),
    path("logout/",LogoutView.as_view(), name="logout"),
    path('refresh-token/', TokenRefreshView.as_view(), name='refresh_token'),  
]    