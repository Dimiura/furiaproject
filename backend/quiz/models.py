from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
import logging
import requests
import traceback

logger = logging.getLogger(__name__)

User = get_user_model()

class FanCard(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='fan_card'
    )
    photo = models.ImageField(
        upload_to='fan_photos/',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Carteirinha de Torcedor"
        verbose_name_plural = "Carteirinhas de Torcedores"

    def __str__(self):
        return f"Carteirinha de {self.user.username}"

class QuizEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    cpf = models.CharField(max_length=14)
    rg = models.CharField(max_length=20)
    buy = models.CharField(max_length=3, choices=[('yes', 'Sim'), ('no', 'Não')])
    buy_details = models.IntegerField(blank=True, null=True)
    attended_event = models.CharField(max_length=3, choices=[('yes', 'Sim'), ('no', 'Não')])
    event_count = models.IntegerField(blank=True, null=True)
    allow_conversation_history = models.BooleanField(default=False)
    accept_lgpd = models.BooleanField()
  
    fan_description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição personalizada do fã"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    fan_level = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('not_fan', 'Não é torcedor'),
            ('regular_fan', 'Torcedor Regular'), 
            ('big_fan', 'Grande fã'),
            ('fanatico', 'Fanático'),
            ('doido_por_furia', 'Doido por FURIA!!')
        ]
    )
    fan_score = models.IntegerField(default=0)

    def get_fan_profile(self):
        return {
            'level': self.get_fan_level_display(),
            'score': self.fan_score,
            'is_hardcore': self.fan_level == 'doido_por_furia'
        }

    def __str__(self):
        return f"{self.full_name} - {self.email}"

from django.contrib.auth.models import User

class TwitterLinkedAccount(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='twitter_account'
    )
    twitter_id = models.CharField(max_length=255, unique=True)
    twitter_username = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255)
    extra_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def fetch_twitter_data(self, force_refresh=False):
        try:
            if not force_refresh and self.extra_data.get('last_updated'):
                last_updated = timezone.datetime.fromisoformat(self.extra_data['last_updated'])
                if (timezone.now() - last_updated).total_seconds() < 3600:
                    return True

            headers = {
                'Authorization': f'Bearer {settings.TWITTER_BEARER_TOKEN.strip()}',
                'User-Agent': 'FuriaFanApp/1.0'
            }

            try:
                search_url = 'https://api.twitter.com/2/tweets/search/recent'
                query = f'from:{self.twitter_username} (@furia OR #furia) -is:retweet'
                params = {
                    'query': query,
                    'max_results': 10,
                    'tweet.fields': 'text,created_at'
                }

                response = requests.get(search_url, headers=headers, params=params, timeout=15)
                
                if response.status_code == 401:
                    logger.error("Token inválido ou expirado")
                    return False
                if response.status_code == 429:
                    logger.warning("Rate limit atingido")
                    return False
                
                response.raise_for_status()
                tweets = response.json().get('data', [])

                self.extra_data = {
                    'last_updated': timezone.now().isoformat(),
                    'interactions_count': 1 if tweets else 0,  
                    'furia_interactions': [{
                        'text': tweet['text'],
                        'date': tweet.get('created_at', '')
                    } for tweet in tweets] if tweets else []
                }
                
                self.save()
                return True

            except requests.exceptions.RequestException as e:
                logger.error(f"Erro na requisição: {str(e)}")
                return False

        except Exception as e:
            logger.error(f"Erro ao buscar dados Twitter: {str(e)}")
            return False

    def __str__(self):
        return f"{self.user.username} -> @{self.twitter_username}"