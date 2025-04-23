from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Exists, OuterRef
from django.contrib.auth import get_user_model

from .models import Conversation, Message, Notification
from .serializers import (
    ConversationSerializer,
    ConversationCreateSerializer,
    MessageSerializer,
    MessageCreateSerializer,
    NotificationSerializer
)

User = get_user_model()


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing conversations"""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'participants__name', 'participants__email']
    ordering_fields = ['updated_at', 'created_at']
    ordering = ['-updated_at']

    def get_queryset(self):
        """Return only conversations where user is a participant"""
        return Conversation.objects.filter(
            participants=self.request.user
        ).annotate(
            unread_messages=Count(
                'messages',
                filter=~Q(messages__read_by=self.request.user) & ~Q(messages__sender=self.request.user)
            )
        ).order_by('-updated_at')

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark all messages in conversation as read"""
        conversation = self.get_object()
        unread_messages = conversation.messages.exclude(read_by=request.user)
        
        for message in unread_messages:
            message.read_by.add(request.user)
        
        return Response({'status': 'messages marked as read'})


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing messages"""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only messages from conversations user is part of"""
        conversation_id = self.kwargs.get('conversation_pk')
        if conversation_id:
            return Message.objects.filter(
                conversation_id=conversation_id,
                conversation__participants=self.request.user
            )
        return Message.objects.filter(conversation__participants=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def create(self, request, *args, **kwargs):
        """Create a new message"""
        # Set conversation from URL if not provided
        conversation_id = self.kwargs.get('conversation_pk')
        if conversation_id and 'conversation' not in request.data:
            request.data['conversation'] = conversation_id
            
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None, conversation_pk=None):
        """Mark a message as read"""
        message = self.get_object()
        message.read_by.add(request.user)
        return Response({'status': 'message marked as read'})


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for managing notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return only user's notifications"""
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a notification as read"""
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response({'status': 'notification marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        self.get_queryset().update(read=True)
        return Response({'status': 'all notifications marked as read'})
