from django.db import models
from django.conf import settings
from core.models import TimeStampedModel


class Conversation(TimeStampedModel):
    """A conversation between two users"""
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='conversations'
    )
    title = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation {self.id}: {self.title}"
    
    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()


class Message(TimeStampedModel):
    """A message within a conversation"""
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    read_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='read_messages',
        blank=True
    )
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message {self.id} from {self.sender.name}"
    
    @property
    def is_read(self):
        """Check if message has been read by all participants"""
        participants = self.conversation.participants.all()
        return all(participant in self.read_by.all() for participant in participants if participant != self.sender)


class Notification(TimeStampedModel):
    """System notification for a user"""
    NOTIFICATION_TYPES = (
        ('MESSAGE', 'New Message'),
        ('REVIEW', 'New Review'),
        ('PAYMENT', 'Payment Update'),
        ('SYSTEM', 'System Notification'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    content = models.TextField()
    read = models.BooleanField(default=False)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} notification for {self.user.email}"
