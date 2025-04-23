from django.contrib import admin
from .models import Conversation, Message, Notification


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['sender', 'content', 'created_at', 'updated_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'get_participants', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'participants__email', 'participants__name']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['participants']
    inlines = [MessageInline]
    
    def get_participants(self, obj):
        return ", ".join([user.email for user in obj.participants.all()])
    get_participants.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender', 'content_preview', 'created_at', 'is_read']
    list_filter = ['created_at', 'sender']
    search_fields = ['content', 'sender__email', 'sender__name']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['read_by']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'notification_type', 'title', 'read', 'created_at']
    list_filter = ['notification_type', 'read', 'created_at']
    search_fields = ['title', 'content', 'user__email', 'user__name']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['read']
