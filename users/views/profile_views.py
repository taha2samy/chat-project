from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.serializers import UserSerializer, GroupMembershipSerializer, ChatGroupSerializer, FriendshipSerializer
from users.models import GroupMembership, Friendship, ChatGroup

# User Profile View
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Serialize the user profile
        user_serializer = UserSerializer(
            user,
            exclude_fields=["user_permissions", "groups", 'password', "is_superuser", "is_staff", "is_active"]
        )

        # Fetch and serialize all groups the user is a member of
        group_memberships = GroupMembership.objects.filter(user=user)
        groups = ChatGroup.objects.filter(groupmembership__user=user).distinct()

        group_data = []
        for group in groups:
            memberships_in_group = GroupMembership.objects.filter(group=group).exclude(user=user.id)
            group_serializer = ChatGroupSerializer(group)
            members_serializer = GroupMembershipSerializer(memberships_in_group, many=True)
            group_data.append({"meta_data": group_serializer.data, 'members': members_serializer.data})

        # Fetch all friendships involving the user
        friendships = Friendship.objects.filter(from_user=user) | Friendship.objects.filter(to_user=user)
        friendships = friendships.exclude(status="rejected")

        processed_friends = []
        for friendship in friendships:
            friend = friendship.to_user if friendship.from_user == user else friendship.from_user
            processed_friends.append({
                'id': friendship.id,
                'friend': {'id': friend.id, 'username': friend.username},
                'status': friendship.status,
                'date_created': friendship.date_created,
            })

        friendship_serializer = FriendshipSerializer(processed_friends, many=True)

        return Response({
            'user_profile': user_serializer.data,
            'groups': group_data,
            'friendships': friendship_serializer.data,
        })
