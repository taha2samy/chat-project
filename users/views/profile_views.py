from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.serializers import UserSerializer, GroupMembershipSerializer, ChatGroupSerializer, FriendshipSerializer
from users.models import GroupMembership, Friendship, ChatGroup
from django.db.models import Q

import logging

# Set up logging
logger = logging.getLogger("users")

def get_all_friends(user, selected_columns=None):
    """
    Fetch all friends of a user with their relationships, optimized using Q objects,
    and allowing selection of specific columns.

    Args:
        user: The user whose friends are to be fetched.
        selected_columns (list): List of columns to include in the result.
                                 Default is ['id', 'friend', 'status', 'date_created'].

    Returns:
        list: A list of dictionaries containing friendship data.
    """
    # Set default columns if not specified
    if selected_columns is None:
        selected_columns = ['id', 'friend', 'status', 'date_created']

    # Fetch friendships using a single query with Q objects
    friendships = Friendship.objects.filter(
        Q(from_user=user.id) | Q(to_user=user.id)
    ).exclude(status="rejected").select_related('from_user', 'to_user')

    processed_friends = []

    for friendship in friendships:
        # Determine the friend user
        friend = friendship.to_user if friendship.from_user == user else friendship.from_user

        # Prepare the friend dictionary dynamically based on selected_columns
        friend_data = {}
        if 'id' in selected_columns:
            friend_data['id'] = friendship.id
        if 'friend' in selected_columns or any(col.startswith('friend.') for col in selected_columns):
            # Include friend details if 'friend' or its subfields are requested
            friend_data['friend'] = {}
            if 'friend.id' in selected_columns or 'friend' in selected_columns:
                friend_data['friend']['id'] = friend.id
            if 'friend.username' in selected_columns or 'friend' in selected_columns:
                friend_data['friend']['username'] = friend.username
        if 'status' in selected_columns:
            friend_data['status'] = friendship.status
        if 'date_created' in selected_columns:
            friend_data['date_created'] = friendship.date_created.isoformat()  # Ensure date is serializable

        # Remove empty 'friend' dictionary if no subfields are selected
        if 'friend' in friend_data and not friend_data['friend']:
            del friend_data['friend']

        processed_friends.append(friend_data)

    return processed_friends
    
# User Profile View
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        logger.warning(f"|||||{user}||||||")
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
            logger.warning("==================")

            # Fetch all friendships involving the user
            processed_friends=get_all_friends(user)
            friendship_serializer = FriendshipSerializer(processed_friends, many=True)

            # Log the successful response
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
