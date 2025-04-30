from rest_framework import serializers
from .models import QuizEntry

class QuizEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizEntry
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
            'validation_result': {'read_only': True},
            'validation_details': {'read_only': True}
        }