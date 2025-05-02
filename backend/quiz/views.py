import json
import logging
import requests
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.conf import settings
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
from .models import QuizEntry, TwitterLinkedAccount
from .serializers import QuizEntrySerializer
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)

class QuizEntryCreateView(generics.CreateAPIView):

    queryset = QuizEntry.objects.all()
    serializer_class = QuizEntrySerializer
    permission_classes = [IsAuthenticated]

    SCORE_WEIGHTS = {
        'events': {'base': 10, 'bonus_threshold': 3, 'bonus': 30},
        'purchases': 20,
        'follows': 15,
        'interactions': {'per_tweet': 5, 'max': 25},
        'chat': {'base': 1, 'bonus_threshold': 20, 'bonus': 20}
    }

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        logger.info("=== INÍCIO DA REQUISIÇÃO ===")
        logger.info(f"Usuário: {request.user}")
        logger.info(f"Método: {request.method}")
        
        try:
            files = request.FILES.getlist('documents')
            logger.info(f"Arquivos recebidos: {[f.name for f in files]}")
            logger.info(f"Tamanho dos arquivos: {[f.size for f in files]}")
            logger.info(f"Tipos MIME: {[f.content_type for f in files]}")

            if not (1 <= len(files) <= 2):
                return Response(
                    {"error": "Envie 1 ou 2 arquivos (frente e/ou verso)."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            for file in files:
                if not file.content_type.startswith(('image/', 'application/pdf')):
                    return Response(
                        {"error": "Apenas imagens ou PDFs são aceitos."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            data = request.data.copy()
            social_links = data.get('social_links', {})
            
            if isinstance(social_links, str):
                try:
                    social_links = json.loads(social_links)
                except json.JSONDecodeError:
                    social_links = {}

            data['social_links'] = social_links

            logger.info("Iniciando validação por IA...")
            validation_result = self.validate_with_ai(files, data)
            logger.info(f"Resultado da validação: {validation_result}")

            if not validation_result["valid"]:
                return Response(
                    {
                        "error": "Falha na validação dos documentos",
                        "validation_details": validation_result.get("details"),
                        "ai_response": validation_result.get("ai_response")
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            return Response({
                "success": True,
                "data": serializer.data,
                "validation_result": validation_result
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Erro ao processar o POST: {str(e)}", exc_info=True)
            return Response(
                {"error": "Erro ao processar sua solicitação."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def extract_text_from_file(self, file):
        try:
            logger.info(f"Processando arquivo: {file.name} ({file.content_type})")
            text = ""
            
            if file.content_type == 'application/pdf':
                images = convert_from_bytes(file.read())
                for img in images:
                    text += pytesseract.image_to_string(img, lang="por")
            else:
                image = Image.open(file)
                text = pytesseract.image_to_string(image, lang="por")
            
            logger.debug(f"Texto extraído (início): {text[:200]}...")
            return text
        except Exception as e:
            logger.error(f"Erro ao extrair texto: {str(e)}")
            raise

    def evaluate_fan_level(self, quiz_data, twitter_data, chat_message_count=0):
        score = 0
        criteria = {
            'has_events': False,
            'has_purchases': False,
            'follows_furia': False,
            'interacts_furia': False,
            'active_chat': False
        }
        
        try:
            events = int(quiz_data.get('event_count', 0)) if str(quiz_data.get('event_count', '0')).isdigit() else 0
            chat_msg_count = int(chat_message_count) if str(chat_message_count).isdigit() else 0
        except (ValueError, TypeError) as e:
            logger.error(f"Erro na conversão de valores: {str(e)}")
            events = 0
            chat_msg_count = 0
        
        if quiz_data.get('attended_event') == 'yes' and events > 0:
            if events >= self.SCORE_WEIGHTS['events']['bonus_threshold']:
                criteria['has_events'] = True
                score += self.SCORE_WEIGHTS['events']['bonus']
            else:
                score += events * self.SCORE_WEIGHTS['events']['base']

        if quiz_data.get('buy') == 'yes':
            criteria['has_purchases'] = True
            score += self.SCORE_WEIGHTS['purchases']
        
        if twitter_data and any('furia' in f.lower() for f in twitter_data.get('following', [])):
            criteria['follows_furia'] = True
            score += self.SCORE_WEIGHTS['follows']
        
        if twitter_data:
            furia_tweets = len([t for t in twitter_data.get('tweets', []) if 'furia' in t.lower()])
            if furia_tweets > 0:
                criteria['interacts_furia'] = True
                score += min(
                    furia_tweets * self.SCORE_WEIGHTS['interactions']['per_tweet'],
                    self.SCORE_WEIGHTS['interactions']['max']
                )
        
        if chat_msg_count >= self.SCORE_WEIGHTS['chat']['bonus_threshold']:
            criteria['active_chat'] = True
            score += self.SCORE_WEIGHTS['chat']['bonus']
        elif chat_msg_count > 0:
            score += min(chat_msg_count, self.SCORE_WEIGHTS['chat']['bonus_threshold'] - 1)
        
        is_hardcore = all(criteria.values())
        
        logger.info(f"Pontuação final: {score} | Critérios: {criteria} | Hardcore: {is_hardcore}")
        
        if is_hardcore:
            return 'hardcore_fan', 100
        elif score >= 70:
            return 'super_fan', score
        elif score >= 45:
            return 'regular_fan', score
        elif score >= 20:
            return 'casual_fan', score
        return 'not_fan', score

    def validate_with_ai(self, files, data):
        try:
            extracted_texts = []
            for f in files:
                try:
                    text = self.extract_text_from_file(f)
                    if text:
                        extracted_texts.append(text)
                except Exception as e:
                    logger.error(f"Erro ao processar arquivo {f.name}: {str(e)}")
                    return {
                        "valid": False,
                        "error": f"Erro ao processar {f.name}",
                        "details": str(e)
                    }
            
            combined_text = "\n".join(extracted_texts)

            twitter_data = {}
            chat_message_count = 0
            
            if hasattr(self.request.user, 'twitter_account'):
                twitter_data = self.request.user.twitter_account.extra_data
            
            if hasattr(self.request.user, 'chathistory'):
                chat_message_count = self.request.user.chathistory.message_count

            fan_level, fan_score = self.evaluate_fan_level(
                data, 
                twitter_data,
                chat_message_count
            )

            prompt = f"""
            Por favor, analise os seguintes dados e retorne um JSON válido com:
            1. Validação dos documentos
            2. Análise do perfil do torcedor
            3. Recomendações personalizadas

            DADOS PARA ANÁLISE (JSON):
            {{
                "form_data": {{
                    "nome": "{data.get('full_name', 'Não informado')}",
                    "eventos_comparecidos": {data.get('event_count', 0)},
                    "compras_realizadas": "{data.get('buy_details', 'Nenhuma')}",
                    "mensagens_chat": {chat_message_count}
                }},
                "twitter_data": {{
                    "segue_furia": {'true' if any('furia' in f.lower() for f in twitter_data.get('following', [])) else 'false'},
                    "tweets_furia": {len([t for t in twitter_data.get('tweets', []) if 'furia' in t.lower()])}
                }},
                "documentos_texto": "{combined_text[:2000]}"
            }}

            FORMATO DE RESPOSTA (JSON):
            {{
                "valid": boolean,
                "validation_details": string,
                "fan_analysis": {{
                    "level": string,
                    "score": number,
                    "is_hardcore": boolean,
                    "missing_criteria": [string],
                    "strengths": [string],
                    "recommendations": [string]
                }},
                "document_validation": {{
                    "name_match": boolean,
                    "cpf_match": boolean,
                    "rg_match": boolean,
                    "details": string
                }}
            }}
            """

            headers = {
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "HTTP-Referer": "http://localhost:3000",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "openai/gpt-3.5-turbo",
                "response_format": {"type": "json_object"},
                "messages": [
                    {
                        "role": "system",
                        "content": "Você é um especialista em validação de documentos e análise de perfil de torcedores. Sua resposta DEVE SER um JSON válido."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "temperature": 0.2,
                "max_tokens": 1000
            }

            logger.info("Enviando requisição para IA...")
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=45
            )
            
            logger.info(f"Resposta da IA: {response.status_code}")
            response.raise_for_status()
            ai_response = response.json()

            if not isinstance(ai_response, dict) or 'choices' not in ai_response:
                logger.error(f"Resposta da API em formato inválido. Resposta completa: {ai_response}")
                return {
                    "valid": False,
                    "error": "Resposta da API em formato inválido",
                    "details": "Campo 'choices' não encontrado na resposta",
                    "raw_response": ai_response
            }
            
            if not ai_response['choices'] or not isinstance(ai_response['choices'], list):
                logger.error(f"Lista de choices vazia ou inválida. Resposta: {ai_response}")
                return {
                    "valid": False,
                    "error": "Resposta da API incompleta",
                    "details": "Nenhuma choice disponível na resposta",
                    "raw_response": ai_response
            }

            try:
                message_content = ai_response['choices'][0]['message']['content']
                if not message_content:
                    raise ValueError("Conteúdo da mensagem vazio")
                
                validation_data = json.loads(message_content)
                
                if validation_data['fan_analysis']['level'] == 'hardcore_fan':
                    if not validation_data['fan_analysis'].get('is_hardcore', False):
                        validation_data['fan_analysis']['level'] = 'super_fan'
                        validation_data['fan_analysis']['score'] = min(90, fan_score)

                return {
                    "valid": validation_data.get("valid", False),
                    "validation_details": validation_data.get("validation_details", ""),
                    "fan_analysis": validation_data.get("fan_analysis", {
                        "level": fan_level,
                        "score": fan_score,
                        "is_hardcore": False,
                        "missing_criteria": [],
                        "recommendations": []
                    }),
                    "document_validation": validation_data.get("document_validation", {}),
                    "raw_ai_response": ai_response
                }

            except (KeyError, json.JSONDecodeError, ValueError) as e:
                logger.error(f"Erro ao decodificar resposta: {str(e)}. Resposta completa: {ai_response}")
                return {
                    "valid": False,
                    "error": "Resposta da IA em formato inválido",
                    "details": str(e),
                    "raw_response": ai_response
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"Falha na requisição: {str(e)}")
            return {
                "valid": False,
                "error": "Falha na conexão com o serviço de validação",
                "details": str(e),
                "response_status": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }

        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
            return {
                "valid": False,
                "error": "Erro interno na validação",
                "details": str(e)
            }

class QuizEntryCheckView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            entry = QuizEntry.objects.filter(user=request.user).first()
            if entry:
                serializer = QuizEntrySerializer(entry)
                return Response({
                    'exists': True,
                    'entry': serializer.data,
                    'fan_level': entry.fan_level, 
                    'fan_score': entry.fan_score
                })
            return Response({'exists': False})
        except Exception as e:
            logger.error(f"Erro ao verificar cadastro: {str(e)}")
            return Response(
                {'error': 'Erro ao verificar cadastro existente'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )            

class QuizEntryUpdateView(generics.UpdateAPIView):
    queryset = QuizEntry.objects.all()
    serializer_class = QuizEntrySerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return QuizEntry.objects.get(user=self.request.user)
    
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)            

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_twitter_validation(request):
  
    try:
        twitter_account = TwitterLinkedAccount.objects.get(user=request.user)
        
        if not twitter_account.fetch_twitter_data():
            return Response(
                {'error': 'Falha ao atualizar dados do Twitter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        quiz_entry = QuizEntry.objects.get(user=request.user)
        
        validation_result = evaluate_fan_level(
            quiz_entry.__dict__,
            twitter_account.extra_data,
            request.user.chathistory.message_count if hasattr(request.user, 'chathistory') else 0
        )
        
        quiz_entry.fan_level = validation_result[0]
        quiz_entry.fan_score = validation_result[1]
        quiz_entry.save()
        
        return Response({
            'success': True,
            'new_level': validation_result[0],
            'new_score': validation_result[1],
            'twitter_data': {
                'follows_furia': twitter_account.extra_data.get('follows_furia', False),
                'tweets_count': twitter_account.extra_data.get('tweets_count', 0),
                'last_updated': twitter_account.extra_data.get('last_updated')
            }
        })
        
    except TwitterLinkedAccount.DoesNotExist:
        return Response(
            {'error': 'Conta do Twitter não vinculada'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except QuizEntry.DoesNotExist:
        return Response(
            {'error': 'Cadastro não encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Erro no refresh: {str(e)}")
        return Response(
            {'error': 'Erro interno no servidor'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def check_ai_status(request):
    try:
        response = requests.get("https://api.openai.com/v1/models", headers={
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}"
        }, timeout=5)
        return Response({"status": "operational" if response.ok else "unavailable"})
    except Exception as e:
        return Response({"status": "error", "details": str(e)})


