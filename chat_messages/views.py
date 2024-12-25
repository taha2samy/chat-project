from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import MessageStatus,Message, Friendship
from .serializers import MessageStatusSerializer
import logging

# Set up logging
logger = logging.getLogger("chat_messages")
# Pagination class
class CustomPagination(PageNumberPagination):
    page_size = 10  # Default page size
    page_size_query_param = 'page_size'
    max_page_size = 100

class MessageStatusView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageStatusSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        
        user = self.request.user
        friendship_id = self.kwargs['friendship_id']  # Take friendship_id from URL parameter
        after = self.request.query_params.get('after')  # Get 'after' flag
        before = self.request.query_params.get('before')  # Get 'before' flag
        start_date = self.request.query_params.get('start_date')  # Start date filter
        start_message_id = self.request.query_params.get('message_id')  # Start message_id filter

        # Ensure only one filter is provided (either 'after' or 'before', not both)
        if (after and before) or (not after and not before):
            return MessageStatus.objects.none()  # If both or neither are provided, return an empty queryset
        
        # Ensure only one filter (either start_date or start_message_id)
        if start_date and start_message_id:
            return MessageStatus.objects.none()  # If both are provided, return an empty queryset
        
        # Find the Friendship object
        try:
            friendship = Friendship.objects.get(id=friendship_id)
            if not (str(friendship.to_user_id) == user.id or str(friendship.from_user_id) == user.id):
                raise friendship.DoesNotExist
        except Friendship.DoesNotExist:
            return MessageStatus.objects.none()  # If no friendship is found

        # Start building the queryset for message statuses related to the given friendship
        queryset = MessageStatus.objects.filter(message__friendship=friendship)
        # Handle filter logic based on 'start_date' and 'start_message_id'
        if start_date:
            if after:
                queryset = queryset.filter(message__created_at__gte=start_date)  # After start_date
            elif before:
                queryset = queryset.filter(message__created_at__lte=start_date)  # Before start_date

        if start_message_id:
            try:
                message = Message.objects.get(id=start_message_id)
                if after:
                    queryset = queryset.filter(message__created_at__gte=message.created_at)  # After or equal to message_id
                elif before:
                    queryset = queryset.filter(message__created_at__lte=message.created_at)  # Before or equal to message_id
            except Message.DoesNotExist:
                return MessageStatus.objects.none()  # If the message doesn't exist

        # Order by created_at (most recent first by default)
        if before:
            queryset = queryset.order_by('-message__created_at')  # Order by oldest first if 'before' is true
        else:
            queryset = queryset.order_by('message__created_at')  # Order by most recent first if 'after' or neither is true

        return queryset

    def list(self, request, *args, **kwargs):
        statuses = self.get_queryset()
        page = self.paginate_queryset(statuses)
        logger.warning(f"{request.user.id}")
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # Update the `is_received` field only for the paginated items where sender.id != user.id
            self.mark_as_received(page, request.user.id)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(statuses, many=True)
        # Update the `is_received` field only for the returned statuses with sender.id != user.id
        self.mark_as_received(statuses, request.user.id)

        return Response(serializer.data)
    def mark_as_received(self, statuses, user_id):
        """
        Marks `is_received` as True for statuses where the message sender is not the requesting user.
        """
        s=MessageStatus.objects.filter(
            id__in=[status.id for status in statuses]
        ).exclude(message__sender__id=user_id)
        s.update(is_received=True)
        logger.warning(f"s \n {user_id} \n \n {[str(status.id) for status in statuses]}")

