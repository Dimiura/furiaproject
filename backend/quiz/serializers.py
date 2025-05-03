from rest_framework import serializers
from .models import QuizEntry, TwitterLinkedAccount, FanCard

class TwitterAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwitterLinkedAccount
        fields = ['twitter_username', 'extra_data']
        read_only_fields = fields


class FanCardSerializer(serializers.ModelSerializer):

    class Meta:
        model = FanCard
        fields = ['id', 'photo', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_photo(self, obj):
        if obj.photo:
            return obj.photo.url
        return None

class QuizEntrySerializer(serializers.ModelSerializer):
    twitter_account = TwitterAccountSerializer(source='user.twitter_account', read_only=True)
    
    class Meta:
        model = QuizEntry
        fields = '__all__'
        extra_kwargs = {
            'full_name': {'required': True},
            'email': {'required': True},
            'cpf': {'required': True},
            'rg': {'required': True},
            'buy': {'required': True},
            'attended_event': {'required': True},
            'accept_lgpd': {'required': True},
            'validation_result': {'read_only': True},
            'validation_details': {'read_only': True},
            'fan_level': {'read_only': True},
            'fan_score': {'read_only': True},
            'allow_conversation_history': {'required': False, 'default': False},
        }

    def validate(self, data):
        data['allow_conversation_history'] = data.get('allow_conversation_history', False)
        return data    
    
    def validate_cpf(self, value):
        if not value.replace('.', '').replace('-', '').isdigit():
            raise serializers.ValidationError("CPF deve conter apenas números")
        return value