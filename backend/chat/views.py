from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
import google.generativeai as genai
from rest_framework import serializers
from rest_framework.generics import ListCreateAPIView
from .models import ChatHistory
from .serializers import ChatHistorySerializer


class ChatBotView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        messages = request.data.get('messages', [])

        user_message = next(
            (msg['content'] for msg in reversed(messages) if msg['role'] == 'user'),
            None
        )

        if not user_message:
            return Response({"reply": "Envie sua pergunta sobre a FURIA!"})

        genai.configure(api_key=settings.GEMINI_API_KEY)

        system_instruction = (
            "Você é o FuriosoBOT, um bot especialista e fã número 1 da equipe de Counter-Strike da FURIA Esports. "
            "Sempre traga informações atualizadas, como a lineup atual, desempenho nos últimos campeonatos, mudanças recentes no time, posição no ranking e notícias relevantes. "
            "Sua resposta deve ser em tom conversacional, como se estivesse trocando ideia com outro fã de CS. Seja direto, informal e entusiasmado. "
            "Fale como um verdadeiro torcedor da FURIA, mas sem perder a clareza. Responda em português e atualize as informações sempre que possível com base nas últimas notícias disponíveis na internet. "
            "Seja objetivo, mas com emoção. E se tiver algum detalhe importante sobre o coach, estratégia, mudança na lineup ou vitória marcante, comenta também!"
        )

        model = genai.GenerativeModel(
            "gemini-1.5-pro-latest",
            system_instruction=system_instruction
        )

        try:
            response = model.generate_content(user_message)
            reply = response.text

            ChatHistory.objects.create(
                user_message=user_message,
                bot_response=reply
            )

        except Exception as e:
            reply = f"Erro ao gerar resposta: {str(e)}"

        return Response({"reply": reply})
    

class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory
        fields = ['id', 'user_message', 'bot_response', 'timestamp']

class ChatHistoryView(ListCreateAPIView):
    queryset = ChatHistory.objects.all().order_by('-timestamp')  
    serializer_class = ChatHistorySerializer        