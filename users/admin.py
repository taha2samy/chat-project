from django.contrib import admin

from django.contrib import admin
from .models import User, ChatGroup, GroupMembership,Friendship

# register the Friendship
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_user','to_user')

admin.site.register(Friendship, FriendshipAdmin)
# Register the User model
class UserAdmin(admin.ModelAdmin):
    list_display = ("id",'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'date_joined')

admin.site.register(User, UserAdmin)

# Register the Group model
class GroupAdmin(admin.ModelAdmin):
    list_display = ("id",'name', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')

admin.site.register(ChatGroup, GroupAdmin)

# Register the GroupMembership model
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'role', 'date_joined')
    search_fields = ('user__username', 'group__name')
    list_filter = ('role', 'date_joined')

admin.site.register(GroupMembership, GroupMembershipAdmin)
