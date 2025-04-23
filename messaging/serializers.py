from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message, Notification

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Simplified user serializer for messaging"""
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for messages"""
    sender = UserBasicSerializer(read_only=True)
    is_read = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'created_at', 'is_read']
        read_only_fields = ['created_at']


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversations"""
    participants = UserBasicSerializer(many=True, read_only=True)
    last_message = MessageSerializer(read_only=True)
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'title', 'created_at', 'updated_at', 'last_message', 'unread_count']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_unread_count(self, obj):
        """Get count of unread messages for the current user"""
        user = self.context['request'].user
        return obj.messages.exclude(read_by=user).exclude(sender=user).count()


class ConversationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new conversation"""
    participants = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True
    )
    initial_message = serializers.CharField(write_only=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'title', 'initial_message']
    
    def validate_participants(self, participants):
        """Ensure current user is included in participants"""
        user = self.context['request'].user
        if user not in participants:
            participants.append(user)
        return participants
    
    def create(self, validated_data):
        """Create conversation and initial message"""
        initial_message = validated_data.pop('initial_message')
        participants = validated_data.pop('participants')
        
        conversation = Conversation.objects.create(**validated_data)
        conversation.participants.set(participants)
        
        # Create the first message
        Message.objects.create(
            conversation=conversation,
            sender=self.context['request'].user,
            content=initial_message
        )
        
        return conversation


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new message"""
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'content']
    
    def validate_conversation(self, conversation):
        """Ensure user is a participant in the conversation"""
        user = self.context['request'].user
        if user not in conversation.participants.all():
            raise serializers.ValidationError("You are not a participant in this conversation")
        return conversation
    
    def create(self, validated_data):
        """Create message and mark as read by sender"""
        message = Message.objects.create(
            conversation=validated_data['conversation'],
            sender=self.context['request'].user,
            content=validated_data['content']
        )
        message.read_by.add(self.context['request'].user)
        
        # Create notification for other participants
        for participant in message.conversation.participants.all():
            if participant != self.context['request'].user:
                Notification.objects.create(
                    user=participant,
                    notification_type='MESSAGE',
                    title=f"New message from {self.context['request'].user.name}",
                    content=f"{self.context['request'].user.name} sent you a message",
                    related_object_id=message.conversation.id,
                    related_object_type='conversation'
                )
        
        return message


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'content', 'created_at', 'read', 
                  'related_object_id', 'related_object_type']
        read_only_fields = ['created_at']
