from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import get_user_model
import requests
from urllib.parse import urlencode
import base64
import hashlib
import secrets
import json
import traceback
from .models import TwitterLinkedAccount
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, HttpRequest

User = get_user_model()

def generate_pkce():
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().replace('=', '')
    return code_verifier, code_challenge

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def twitter_auth_start(request):
    """Inicia o fluxo OAuth2 com PKCE"""
    try:
        code_verifier, code_challenge = generate_pkce()
        state = str(request.user.id)
        
        if 'twitter_verifiers' not in request.session:
            request.session['twitter_verifiers'] = {}
        request.session['twitter_verifiers'][state] = code_verifier
        request.session.modified = True
        
        params = {
            'response_type': 'code',
            'client_id': settings.SOCIALACCOUNT_PROVIDERS['twitter']['APP']['client_id'],
            'redirect_uri': 'http://localhost:8000/api/v1/quiz/auth/twitter/callback/',
            'scope': 'tweet.read users.read',
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }
        
        auth_url = f"https://twitter.com/i/oauth2/authorize?{urlencode(params)}"
        return Response({
            'auth_url': auth_url,
            'state': state,
            'popup_width': 600,
            'popup_height': 700
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@csrf_exempt
def twitter_auth_callback(request: HttpRequest):
    try:
        code = request.GET.get('code')
        state = request.GET.get('state')
        
        print(f"Received callback - code: {code}, state: {state}")
        
        if not code or not state:
            print("Missing params in callback")
            return HttpResponseRedirect('http://localhost:3000/error?reason=missing_params')

        code_verifier = None
        if 'twitter_verifiers' in request.session and state in request.session['twitter_verifiers']:
            code_verifier = request.session['twitter_verifiers'].pop(state)
            request.session.modified = True
            
        if not code_verifier:
            print("Code verifier not found in session")
            return HttpResponseRedirect('http://localhost:3000/error?reason=missing_code_verifier')

        token_url = 'https://api.twitter.com/2/oauth2/token'
        
        client_id = settings.SOCIALACCOUNT_PROVIDERS['twitter']['APP']['client_id']
        client_secret = settings.SOCIALACCOUNT_PROVIDERS['twitter']['APP']['secret']
        auth_string = f"{client_id}:{client_secret}"
        basic_auth = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {basic_auth}'
        }

        data = {
            'code': code,
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'redirect_uri': 'http://localhost:8000/api/v1/quiz/auth/twitter/callback/',
            'code_verifier': code_verifier
        }

        print("Making token request to Twitter...")
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()

        headers = {'Authorization': f'Bearer {token_data["access_token"]}'}
        user_info = requests.get(
            'https://api.twitter.com/2/users/me?user.fields=username,id',
            headers=headers
        ).json()
        
        existing_account = TwitterLinkedAccount.objects.filter(user_id=state).first()
        
        defaults = {
            'twitter_id': user_info['data']['id'],
            'twitter_username': user_info['data']['username'],
            'access_token': token_data['access_token']
        }
        
        if existing_account:
            defaults['extra_data'] = {
                **existing_account.extra_data,  
                'auth_info': {                
                    'id': user_info['data']['id'],
                    'username': user_info['data']['username'],
                    'name': user_info['data'].get('name', '')
                }
            }
        else:
            defaults['extra_data'] = {
                'auth_info': {
                    'id': user_info['data']['id'],
                    'username': user_info['data']['username'],
                    'name': user_info['data'].get('name', '')
                },
                'interactions': {
                    'last_updated': None,
                    'count': 0,
                    'tweets': []
                }
            }
        
        account, created = TwitterLinkedAccount.objects.update_or_create(
            user_id=state,
            defaults=defaults
        )
        
        return HttpResponseRedirect('http://localhost:3000/?twitter_linked=true&username=' + user_info['data']['username'])
        
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return HttpResponseRedirect('http://localhost:3000/error?reason=twitter_auth_failed')
    except Exception as e:
        print(f"Other error occurred: {str(e)}")
        traceback.print_exc()
        return HttpResponseRedirect('http://localhost:3000/error?reason=server_error')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_twitter_status(request):
    try:
        twitter_account = TwitterLinkedAccount.objects.get(user=request.user)
        return Response({
            'linked': True,
            'username': twitter_account.twitter_username,
            'extra_data': twitter_account.extra_data
        })
    except TwitterLinkedAccount.DoesNotExist:
        return Response({'linked': False})