from rest_framework import serializers
from .models import ChatHistory

class ChatHistorySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ChatHistory
        fields = ['id', 'user', 'user_message', 'bot_response', 'timestamp']  
        read_only_fields = ['user'] 