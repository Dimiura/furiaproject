from rest_framework import serializers
from .models import QuizEntry, TwitterLinkedAccount

class TwitterAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwitterLinkedAccount
        fields = ['twitter_username', 'extra_data']
        read_only_fields = fields

class QuizEntrySerializer(serializers.ModelSerializer):
    twitter_account = TwitterAccountSerializer(source='user.twitter_account', read_only=True)
    
    class Meta:
        model = QuizEntry
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
            'validation_result': {'read_only': True},
            'validation_details': {'read_only': True},
            'fan_level': {'read_only': True},
            'fan_score': {'read_only': True}
        }
    
    def validate_cpf(self, value):
        if not value.replace('.', '').replace('-', '').isdigit():
            raise serializers.ValidationError("CPF deve conter apenas números")
        return value