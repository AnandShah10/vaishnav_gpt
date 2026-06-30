from django.db import models
from django.utils import timezone


class Message(models.Model):
    user_message = models.TextField()
    bot_reply = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user_message[:50]}..."
    
    class Meta:
        ordering = ['-timestamp']
