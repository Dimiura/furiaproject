from django.db import models
from django.utils.timezone import now

class ChatHistory(models.Model):
    user_message = models.TextField()  
    bot_response = models.TextField()  
    timestamp = models.DateTimeField(auto_now_add=True) 

    def save(self, *args, **kwargs):
        self.timestamp = now() 
        super().save(*args, **kwargs)
    
class Message(models.Model):
    chat = models.ForeignKey(ChatHistory, related_name="messages", on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=[("user", "User"), ("assistant", "Assistant")])
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.id} in Chat {self.chat.id}"