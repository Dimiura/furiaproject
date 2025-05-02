from django.urls import path, include
from .views import QuizEntryCreateView, QuizEntryCheckView, QuizEntryUpdateView, refresh_twitter_validation
from .views_oauth import (
    twitter_auth_start,
    twitter_auth_callback,
    check_twitter_status,
)
from . import views

urlpatterns = [
    path('formulario/', QuizEntryCreateView.as_view(), name='quiz-formulario'),
    path('ai-status/', views.check_ai_status, name='ai-status'),
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    
    path('auth/twitter/start/', twitter_auth_start, name='twitter_auth_start'),
    path('auth/twitter/callback/', twitter_auth_callback, name='twitter_auth_callback'),
    path('auth/twitter/status/', check_twitter_status, name='twitter_status'),
    path('check-entry/', QuizEntryCheckView.as_view(), name='quiz-check-entry'),
    path('update-entry/', QuizEntryUpdateView.as_view(), name='quiz-update-entry'),
    path('refresh-validation/', refresh_twitter_validation, name='refresh-validation'),
]