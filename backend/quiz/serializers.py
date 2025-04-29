from rest_framework import serializers
from .models import QuizEntry

class QuizEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizEntry
        fields = ['id', 'full_name', 'instagram_handle', 'twitter_handle', 'created_at']
