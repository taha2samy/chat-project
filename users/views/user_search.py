from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer

User = get_user_model()

class UserPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'  
    max_page_size = 100  

class UserListView(ListAPIView):
    serializer_class = UserSerializer
    pagination_class = UserPagination
    permission_classes = [IsAuthenticated]  

    def get_queryset(self):
        username = self.request.query_params.get('username', None)
        if username:
            return User.objects.filter(username__icontains=username)
        return User.objects.none()  
    def get_serializer(self, *args, **kwargs):
        kwargs['include_fields'] = ["id", "username", "personal_image"]
        return UserSerializer(*args, **kwargs)
