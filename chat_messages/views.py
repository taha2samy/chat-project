from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Media
import logging
from django.db.models import Q


from .models import Message, MessageStatus, ChatMessage, Friendship
from .serializers import MessageStatusSerializer

logger = logging.getLogger("chat_messages")


class FriendshipNotificationSeenView(APIView):
    def post(self, request):
        try:
            id = request.data.get("message_id")
            user = request.user
            message_status = MessageStatus.objects.get(message_id=id, receiver_id=user.id)
            logger.error(f"{id}")
            message_status.is_seen = True
            message_status.save()
            return Response({"success": "Message marked as seen"}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"error": "Message not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




class MessagesPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class to set the page size.
    """
    page_size = 10  # Set the default page size here
    page_size_query_param = 'page_size'  # Allow clients to override the page size
    max_page_size = 100  # Set the maximum page size
class FriendshipMessageAPIView(APIView):
    """
    API View to handle both sending messages (POST) and retrieving message statuses (GET).
    """
    permission_classes = [IsAuthenticated]
    pagination_class = MessagesPageNumberPagination

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to retrieve message statuses.
        Supports filtering by 'after', 'before', 'start_date', or 'start_message_id'.
        """
        user = request.user
        friendship_id = request.data.get("channel")
        after = request.query_params.get("after")
        before = request.query_params.get("before")
        start_date = request.query_params.get("start_date")
        start_message_id = request.query_params.get("message_id")

        # Validate friendship
        try:
            friendship = Friendship.objects.get(id=friendship_id)
            if not (str(friendship.to_user_id) == user.id or str(friendship.from_user_id) == user.id):
                raise ObjectDoesNotExist
        except ObjectDoesNotExist:
            return Response({"error": "Friendship not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)

        # Filter messages
        queryset = MessageStatus.objects.filter(message__friendship=friendship)
        if start_date:
            if after:
                queryset = queryset.filter(message__created_at__gte=start_date)
            elif before:
                queryset = queryset.filter(message__created_at__lte=start_date)
        if start_message_id:
            try:
                message = Message.objects.get(id=start_message_id)
                if after:
                    queryset = queryset.filter(message__created_at__gte=message.created_at)
                elif before:
                    queryset = queryset.filter(message__created_at__lte=message.created_at)
            except Message.DoesNotExist:
                return Response({"error": "Invalid message_id"}, status=status.HTTP_400_BAD_REQUEST)

        # Order results
        queryset = queryset.order_by('-message__created_at') if before else queryset.order_by('message__created_at')

        # Pagination
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = MessageStatusSerializer(page, many=True)
        
        # Mark as received
        self.mark_as_received(page, user.id)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to send a message.
        """
        message_payload = request.data.get("content")
        message_media = request.FILES.getlist("media")
        friendship_id = request.data.get("channel")
        user = request.user

        # Validate friendship
        try:
            friendship = Friendship.objects.get(id=friendship_id)
            if not (str(friendship.to_user_id) == str(user.id) or str(friendship.from_user_id) == str(user.id)):
                return Response({"error": "You are not authorized to send messages to this friendship"}, status=status.HTTP_401_UNAUTHORIZED)
        except Friendship.DoesNotExist:
            return Response({"error": "Friendship not found"}, status=status.HTTP_404_NOT_FOUND)
        # Create message
        try:
            message = Message.objects.create(
                friendship=friendship,
                sender_id=user.id,
                content=message_payload
            )
            if message_media:
                for media_file in message_media:
                    media = Media.objects.create(file=media_file)
                    message.media.add(media)


            message=MessageStatus.objects.create(
                message=message,
                receiver_id=friendship.to_user_id if str(friendship.from_user_id) == str(user.id) else friendship.from_user_id)
            message= MessageStatusSerializer(message).data
            return Response({"success": "Message sent successfully","data":message}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def mark_as_received(self, statuses, user_id):
        """
        Marks `is_received` as True for statuses where the message sender is not the requesting user.
        """
        for status in statuses:
            if status.message.sender_id != user_id:
                status.is_received = True
                status.save()

