from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.core.exceptions import ValidationError

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
      
        if request.user.is_anonymous:
            raise ValidationError("Você deve estar logado para vincular contas")
        
    def save_user(self, request, sociallogin, form=None):
        
        raise ValidationError("Cadastro via redes sociais não é permitido")