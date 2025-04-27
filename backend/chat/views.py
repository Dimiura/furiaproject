from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
import google.generativeai as genai
from rest_framework import serializers
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from .models import ChatHistory, Message
from .serializers import ChatHistorySerializer
import openai
import requests



class ChatBotView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        messages = request.data.get('messages', [])
        chat_id = request.data.get('chat_id', None)

        user_message = next(
            (msg['content'] for msg in reversed(messages) if msg['role'] == 'user'),
            None
        )

        if not user_message:
            return Response({"reply": "Envie sua pergunta sobre a FURIA!"}, status=400)
        
        openai.api_key = settings.OPENAI_API_KEY
        openai.api_base = "https://openrouter.ai/api/v1" 

        system_instruction = (
            "Você é o FuriosoBOT, um bot especialista e fã número 1 da equipe de Counter-Strike da FURIA Esports. "
            "Sempre traga informações atualizadas, como a lineup atual, desempenho nos últimos campeonatos, mudanças recentes no time, posição no ranking e notícias relevantes. "
            "Sua resposta deve ser em tom conversacional, como se estivesse trocando ideia com outro fã de CS. Seja direto, informal e entusiasmado. "
            "Fale como um verdadeiro torcedor da FURIA, mas sem perder a clareza. Responda em português e atualize as informações sempre que possível com base nas últimas notícias disponíveis na internet. "
            "Seja objetivo, mas com emoção. E se tiver algum detalhe importante sobre o coach, estratégia, mudança na lineup ou vitória marcante, comenta também!"
        )

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "openai/gpt-3.5-turbo",  
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_message},
            ]
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            bot_response = data['choices'][0]['message']['content']

            if chat_id:
                try:
                    chat = ChatHistory.objects.get(pk=chat_id)
                except ChatHistory.DoesNotExist:
                    return Response({"error": "Conversa não encontrada"}, status=404)
            else:
                chat = ChatHistory.objects.create(user_message=user_message, bot_response=bot_response)

            Message.objects.create(chat=chat, role="user", content=user_message)
            Message.objects.create(chat=chat, role="assistant", content=bot_response)

        except Exception as e:
            bot_response = f"Erro ao gerar resposta: {str(e)}"

        return Response({"reply": bot_response, "chat_id": chat.id})
    

class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory
        fields = ['id', 'user_message', 'bot_response', 'timestamp']

class ChatHistoryDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            chat = ChatHistory.objects.get(pk=pk)
            messages = chat.messages.order_by('timestamp').values('role', 'content', 'timestamp')
            return Response({"id": chat.id, "messages": list(messages)})
        except ChatHistory.DoesNotExist:
            return Response({"error": "Chat not found"}, status=404)

class NewChatView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return Response({"id": None})
    
class RecentChatHistoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        recent_chats = ChatHistory.objects.order_by('-timestamp')[:5]
        data = [
            {
                "id": chat.id,
                "summary": chat.messages.last().content if chat.messages.exists() else "Sem mensagens ainda",
                "timestamp": chat.timestamp,
            }
            for chat in recent_chats
        ]
        return Response(data)