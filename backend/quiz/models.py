from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

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

    fan_level = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('not_fan', 'Não é torcedor'),
            ('casual_fan', 'Torcedor Casual'), 
            ('regular_fan', 'Torcedor Regular'),
            ('hardcore_fan', 'Torcedor Fanático')
        ]
    )
    fan_score = models.IntegerField(default=0)

    def get_fan_profile(self):
        return {
            'level': self.get_fan_level_display(),
            'score': self.fan_score,
            'is_hardcore': self.fan_level == 'hardcore_fan'
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

    def fetch_twitter_data(self):
        try:
            import requests
            headers = {'Authorization': f'Bearer {self.access_token}'}
            
            user_url = f'https://api.twitter.com/2/users/{self.twitter_id}'
            user_response = requests.get(user_url, headers=headers)
            user_data = user_response.json().get('data', {})
            
            following_url = f'https://api.twitter.com/2/users/{self.twitter_id}/following'
            following_response = requests.get(following_url, headers=headers)
            following = [user['username'] for user in following_response.json().get('data', [])]
            
            tweets_url = 'https://api.twitter.com/2/tweets/search/recent'
            tweets_params = {
                'query': f'from:{self.twitter_username} (furia OR #furia)',
                'max_results': 50
            }
            tweets_response = requests.get(tweets_url, headers=headers, params=tweets_params)
            tweets = [t['text'] for t in tweets_response.json().get('data', [])]
            
            self.extra_data = {
                'last_updated': timezone.now().isoformat(),
                'user_data': user_data,
                'following': following,
                'furia_tweets': tweets,
                'follows_furia': any('furia' in f.lower() for f in following),
                'tweets_count': len(tweets)
            }
            
            self.save()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados do Twitter: {str(e)}")
            return False

    def __str__(self):
        return f"{self.user.username} -> @{self.twitter_username}"