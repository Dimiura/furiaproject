from django.urls import path
from .views import QuizEntryCreateView
from . import views

urlpatterns = [
    path('formulario/', QuizEntryCreateView.as_view(), name='quiz-formulario'),
    path('ai-status/', views.check_ai_status, name='ai-status')
]
