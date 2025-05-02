from django.db import models
from django.utils.timezone import now
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatHistory(models.Model):
    user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name='chats',
    null=True,  
    blank=True
    )
    user_message = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
class Message(models.Model):
    chat = models.ForeignKey(ChatHistory, related_name="messages", on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=[("user", "User"), ("assistant", "Assistant")])
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.id} in Chat {self.chat.id}"