from django.urls import path
from .views import QuizEntryCreateView

urlpatterns = [
    path('', QuizEntryCreateView.as_view(), name='quiz-entry-create'),
]
