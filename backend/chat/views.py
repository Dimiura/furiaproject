from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from rest_framework.permissions import IsAuthenticated, AllowAny
import google.generativeai as genai
from django.db.models import Count, Q
from rest_framework import serializers
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from .models import ChatHistory, Message
from .serializers import ChatHistorySerializer
import openai
import requests
from rest_framework.decorators import api_view, permission_classes



class ChatBotView(APIView):
    permission_classes = [IsAuthenticated]

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

        system_instruction = """
        Você é o FURIA_BOT, especialista em FURIA Esports (CS2/CSGO). Siga À RISCA:
        1. **Fontes**: Só responda com informações de Liquipedia, HLTV, Twitter @FURIA e sites de Esports, busque sempre a fonte mais atual.
        2. **Precisão**: Se não souber, diga: "Vou checar!" e NÃO INVENTE.
        3. **Tom**: Informal (ex.: "FURIA tá voando!"), mas sem enrolação.
        4. **Elenco atual** : FalleN, KSCERATO, yuurih, molodoy, YEKINDAR e sidde (coach).
        5. **Se o usuário corrigir**: "Valeu pelo toque! Conferi e realmente é [X]."

        Exemplo de resposta:
        - "FURIA tá no [campeonato]. Próximo jogo: [data] contra [time]."
        - "Segundo o HLTV, eles venceram [time] por 2-1 ontem."
        """

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",  
            "X-Title": "FURIA Bot"  
        }
        payload = {
            "model": "deepseek/deepseek-chat",  
            "messages": [
                {"role": "system", "content": system_instruction},
                *[msg for msg in messages if msg['role'] in ['user', 'assistant']],  
            ]
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)  
            response.raise_for_status()
            data = response.json()

            bot_response = data['choices'][0]['message']['content']

            if chat_id:
                try:
                    chat = ChatHistory.objects.get(pk=chat_id, user=request.user)  
                except ChatHistory.DoesNotExist:
                    return Response({"error": "Conversa não encontrada"}, status=404)
            else:
                chat = ChatHistory.objects.create(
                    user=request.user,  
                    user_message=user_message, 
                    bot_response=bot_response
                )

            Message.objects.create(chat=chat, role="user", content=user_message)
            Message.objects.create(chat=chat, role="assistant", content=bot_response)

        except requests.exceptions.RequestException as e:  
            bot_response = f"Erro na comunicação com o servidor: {str(e)}"
            return Response({"reply": bot_response, "chat_id": chat_id if chat_id else None}, status=500)
        except Exception as e:
            bot_response = f"Erro ao gerar resposta: {str(e)}"
            return Response({"reply": bot_response, "chat_id": chat_id if chat_id else None}, status=500)

        return Response({"reply": bot_response, "chat_id": chat.id})
    

class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory
        fields = ['id', 'user_message', 'bot_response', 'timestamp']

class ChatHistoryDetailView(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self, request, pk):
        try:
            chat = ChatHistory.objects.get(pk=pk, user=request.user)  # Filtrar por usuário
            messages = chat.messages.order_by('timestamp').values('role', 'content', 'timestamp')
            return Response({"id": chat.id, "messages": list(messages)})
        except ChatHistory.DoesNotExist:
            return Response({"error": "Chat not found"}, status=404)

class NewChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        chat = ChatHistory.objects.create(user=request.user)  # Criar chat associado ao usuário
        return Response({"id": chat.id})
        
class RecentChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        recent_chats = ChatHistory.objects.filter(user=request.user).order_by('-timestamp')[:5]  
        data = [
            {
                "id": chat.id,
                "summary": chat.messages.last().content if chat.messages.exists() else "Sem mensagens ainda",
                "timestamp": chat.timestamp,
            }
            for chat in recent_chats
        ]
        return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def message_count(request):
    
    try:
        counts = Message.objects.filter(
            Q(chat__user=request.user) | Q(chat__user__isnull=True)
        ).aggregate(
            total=Count('id'),
            user_messages=Count('id', filter=Q(role='user')),
            bot_messages=Count('id', filter=Q(role='assistant'))
        )
        
        chat_sessions = ChatHistory.objects.filter(user=request.user).count()
        
        return Response({
            'count': counts['total'],
            'user_messages': counts['user_messages'],
            'bot_messages': counts['bot_messages'],
            'chat_sessions': chat_sessions
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)