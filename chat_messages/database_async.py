from users.models import Friendship
from django.db.models import Q
from users.models import GroupMembership
from channels.db import database_sync_to_async


@database_sync_to_async
def get_all_friendship(user):     
    return list(
        Friendship.objects.filter(
            Q(from_user=user.id) | Q(to_user=user.id)
        ).exclude(status_from_user="rejected", status_to_user="rejected")
        .select_related('from_user', 'to_user')
    )

@database_sync_to_async
def get_all_group(user):
    group_memberships = GroupMembership.objects.filter(user=user)
    return list(group_memberships.values('group_id'))

