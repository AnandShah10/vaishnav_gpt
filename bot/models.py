from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


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

class LearningProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.CharField(max_length=50)
    history = models.JSONField(default=list)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'path')

    def __str__(self):
        return f"{self.user.username} - {self.path}"

class OTP(models.Model):
    email = models.EmailField(unique=True)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now=True)

    def is_valid(self):
        return (timezone.now() - self.created_at).total_seconds() < 300 # 5 minutes

    def __str__(self):
        return f"{self.email} - {self.otp_code}"
