from django.db import models
from django.utils import timezone


class Message(models.Model):
    user_message = models.TextField()
    bot_reply = models.TextField()
    tradition = models.CharField(max_length=20, default='universal', blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user_message[:50]}... ({self.tradition})"
    
    class Meta:
        ordering = ['-timestamp']

class UserFeedback(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    timestamp = models.DateTimeField(default=timezone.now)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.email}"

