from django.urls import path, include
from django.conf.urls.static import static
from .views import QuizEntryCreateView, QuizEntryCheckView, QuizEntryUpdateView, refresh_twitter_validation, FanCardView
from .views_oauth import (
    twitter_auth_start,
    twitter_auth_callback,
    check_twitter_status,
)
from django.conf import settings
from . import views

urlpatterns = [
    path('formulario/', QuizEntryCreateView.as_view(), name='quiz-formulario'),
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    
    path('auth/twitter/start/', twitter_auth_start, name='twitter_auth_start'),
    path('auth/twitter/callback/', twitter_auth_callback, name='twitter_auth_callback'),
    path('auth/twitter/status/', check_twitter_status, name='twitter_status'),
    path('check-entry/', QuizEntryCheckView.as_view(), name='quiz-check-entry'),
    path('update-entry/', QuizEntryUpdateView.as_view(), name='quiz-update-entry'),
    path('refresh-validation/', refresh_twitter_validation, name='refresh-validation'),
    path('fan-card/', FanCardView.as_view(), name='fan-card-detail'),
] 

