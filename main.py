from users.models import GroupMembership
 
import json


from users.views.profile_views import get_all_friends


print([f"{i['id']}r" for i in get_all_friends(1)])