from django.contrib import admin
from .models import Media, Message, MessageStatus

# Customizing the Media Admin
class MediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'uploaded_at')  # Fields to display in the list view
    search_fields = ('id', 'file')  # Fields to enable search
    list_filter = ('uploaded_at',)  # Filter by uploaded date

# Customizing the Message Admin
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'created_at', 'content')
    search_fields = ('sender__username', 'receiver__username', 'content')  # Search by sender, receiver, or content
    list_filter = ('created_at', 'sender', 'receiver')  # Filter by creation date, sender, or receiver
    filter_horizontal = ('media',)  # Allows for a nice interface for adding media files

# Customizing the MessageStatus Admin
class MessageStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'is_seen', 'is_received', 'updated_at')  # Fields to display
    search_fields = ('message__id', 'message__sender__username', 'message__receiver__username')
    list_filter = ('is_seen', 'is_received', 'updated_at')  # Filter by message status or date

# Register the models with the admin interface
admin.site.register(Media, MediaAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(MessageStatus, MessageStatusAdmin)
