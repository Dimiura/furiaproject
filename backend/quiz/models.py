from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class QuizEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    cpf = models.CharField(max_length=14)
    rg = models.CharField(max_length=20)
    buy = models.CharField(max_length=3, choices=[('yes', 'Sim'), ('no', 'Não')])
    buy_details = models.TextField(blank=True, null=True)
    attended_event = models.CharField(max_length=3, choices=[('yes', 'Sim'), ('no', 'Não')])
    event_count = models.IntegerField(blank=True, null=True)
    social_links = models.JSONField(default=dict)
    allow_conversation_history = models.BooleanField(default=False)
    accept_lgpd = models.BooleanField()
    validation_result = models.BooleanField(default=False)
    validation_details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.email}"