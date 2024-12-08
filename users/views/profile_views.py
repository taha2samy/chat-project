from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.serializers import UserSerializer, GroupMembershipSerializer, ChatGroupSerializer, FriendshipSerializer
from users.models import GroupMembership, Friendship, ChatGroup
from django.db.models import Q
from django.contrib.auth import get_user_model

import logging

# Set up logging
logger = logging.getLogger("users")

User=get_user_model()

# User Profile View
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user = User.objects.get(pk=user.id)
        try:
            # Serialize the user profile
            user_serializer = UserSerializer(
                user,
                exclude_fields=["user_permissions", "groups", 'password', "is_superuser", "is_staff", "is_active"]
            )

            # Fetch and serialize all groups the user is a member of
            group_memberships = GroupMembership.objects.filter(id=user.id)
            
            groups = ChatGroup.objects.filter(groupmembership__user=user.id).distinct()
            group_data = []
            for group in groups:
                memberships_in_group = GroupMembership.objects.filter(group=group).exclude(user=user.id)
                group_serializer = ChatGroupSerializer(group)
                members_serializer = GroupMembershipSerializer(memberships_in_group, many=True)
                group_data.append({"meta_data": group_serializer.data, 'members': members_serializer.data})

            friendships = Friendship.objects.filter(
            Q(from_user=user.id) | Q(to_user=user.id)
            ).exclude(status_from_user="rejected",status_to_user="rejected").select_related('from_user', 'to_user')

        
            friendship_serializer = FriendshipSerializer(friendships, many=True)
            logger.warning(friendship_serializer.data)
            logger.info(f"User {user.username} profile fetched successfully.")

            return Response({
                'user_profile': user_serializer.data,
                'groups': group_data,
                'friendships': friendship_serializer.data,
            })

        except Exception as e:
            # Log any unexpected errors
            logger.error(f"----{str(e)}")
            return Response(
                {"error": f"{e}"},
                status=500
            )
