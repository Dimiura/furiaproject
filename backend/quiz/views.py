import json
import logging
import requests
from django.db.models import Q
from chat.models import ChatHistory, Message
from rest_framework import generics, status
from rest_framework.response import Response
from django.conf import settings
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
from .models import QuizEntry, TwitterLinkedAccount, FanCard
from .serializers import QuizEntrySerializer, FanCardSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import os

logger = logging.getLogger(__name__)

SCORE_WEIGHTS = {
    'twitter_interaction': 50,       
    'events': 30,                    
    'purchases': 20,                
    'chat_messages': {
        'base': 0,                   
        'bonus': 20                 
    }
}

FAN_LEVELS = {
    'not_fan': (0, 49),
    'regular_fan': (50, 69),
    'big_fan': (70, 89),
    'fanatico': (90, 100),
    'doido_por_furia': (101, 120)  
}

def evaluate_fan_level(quiz_data, twitter_data, chat_message_count=0, allow_conversation_history=False):
    score = 0
    criteria_met = {
        'twitter_interaction': False,
        'events': False,
        'purchases': False,
        'chat_messages': False
    }
    
    has_twitter_interaction = twitter_data.get('interactions_count', 0) > 0
    if has_twitter_interaction:
        criteria_met['twitter_interaction'] = True
        score += SCORE_WEIGHTS['twitter_interaction']
    
    events = int(quiz_data.get('event_count', 0)) if str(quiz_data.get('event_count', '0')).isdigit() else 0
    if events > 0:
        criteria_met['events'] = True
        score += SCORE_WEIGHTS['events']
    
    if quiz_data.get('buy') == 'yes':
        criteria_met['purchases'] = True
        score += SCORE_WEIGHTS['purchases']
    
    if allow_conversation_history:  
        logger.info(f"Verificando mensagens de chat: {chat_message_count} mensagens (precisa de 3)")
        if chat_message_count >= 3:
            criteria_met['chat_messages'] = True
            score += SCORE_WEIGHTS['chat_messages']['bonus']
            logger.info(f"Bônus de 20 pontos aplicado! Novo score: {score}")
        else:
            logger.info(f"Bônus NÃO aplicado - mensagens insuficientes")

    if score > 100:
        return 'doido_por_furia', min(score, 120)
    elif score >= 90:
        return 'fanatico', min(score, 100)
    elif score >= 70:
        return 'big_fan', min(score, 100)
    elif score >= 50:
        return 'regular_fan', min(score, 100)
    return 'not_fan', min(score, 100)

class QuizEntryCreateView(generics.CreateAPIView):
    queryset = QuizEntry.objects.all()
    serializer_class = QuizEntrySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        self.calculate_initial_score(instance)

    def calculate_initial_score(self, instance):
        twitter_data = {}
        chat_message_count = 0

        try:
            twitter_account = TwitterLinkedAccount.objects.get(user=self.request.user)
            
            try:
                if not twitter_account.fetch_twitter_data(force_refresh=True):
                    logger.warning("Falha ao atualizar dados do Twitter")
            except Exception as e:
                logger.error(f"Erro ao buscar dados do Twitter: {str(e)}")
            
            twitter_data = {
                'interactions_count': twitter_account.extra_data.get('interactions_count', 0)
            }
            
            logger.info(f"Dados do Twitter obtidos: {twitter_data}")
        except TwitterLinkedAccount.DoesNotExist:
            logger.info("Usuário não possui conta do Twitter vinculada")
        except Exception as e:
            logger.error(f"Erro ao acessar conta do Twitter: {str(e)}")
        
        if hasattr(self.request.user, 'twitter_account'):
            twitter_account = self.request.user.twitter_account
            if hasattr(twitter_account, 'extra_data') and twitter_account.extra_data:
                twitter_data = {
                    'interactions_count': twitter_account.extra_data.get('interactions_count', 0)
                }
            else:
                try:
                    twitter_account.fetch_twitter_data()
                    twitter_data = {
                        'interactions_count': twitter_account.extra_data.get('interactions_count', 0)
                    }
                except Exception as e:
                    logger.error(f"Erro ao buscar dados do Twitter: {str(e)}")
        
        if instance.allow_conversation_history:
            try:
                from chat.models import Message
                chat_message_count = Message.objects.filter(
                    chat__user=self.request.user,
                    role='user'
                ).count()
                logger.info(f"Total de mensagens encontradas: {chat_message_count}")
            except Exception as e:
                logger.error(f"Erro ao contar mensagens: {str(e)}")

        quiz_data = {
            'event_count': instance.event_count,
            'buy': instance.buy,
            'buy_details': instance.buy_details,
            'attended_event': 'yes' if instance.event_count and instance.event_count > 0 else 'no'
        }

        fan_level, fan_score = evaluate_fan_level(
            quiz_data,
            twitter_data,
            chat_message_count,
            instance.allow_conversation_history
        )
        
        instance.fan_level = fan_level
        instance.fan_score = fan_score
        instance.save()

    def post(self, request, *args, **kwargs):
        try:
            logger.info(f"Iniciando processamento do POST - Dados recebidos: {request.data}")
            logger.info(f"Arquivos recebidos: {request.FILES}")

            try:
                buy_details = int(request.data.get('buy_details', 0)) if request.data.get('buy_details') else 0
            except (ValueError, TypeError) as e:
                logger.error(f"Erro na conversão de buy_details: {str(e)}")
                return Response(
                    {"error": "O campo buy_details deve ser um número inteiro."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            files = request.FILES.getlist('documents')
            if not (1 <= len(files) <= 2):
                logger.warning(f"Número inválido de arquivos: {len(files)}")
                return Response(
                    {"error": "Envie 1 ou 2 arquivos (frente e/ou verso)."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            for file in files:
                if not file.content_type.startswith(('image/', 'application/pdf')):
                    logger.error(f"Tipo de arquivo inválido: {file.content_type}")
                    return Response(
                        {"error": f"Tipo de arquivo não suportado: {file.content_type}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            data = {
                'user': request.user.id,
                'full_name': request.data.get('full_name'),
                'email': request.data.get('email'),
                'cpf': request.data.get('cpf', ''),
                'rg': request.data.get('rg', ''),
                'buy': request.data.get('buy'),
                'buy_details': buy_details,
                'attended_event': request.data.get('attended_event'),
                'event_count': request.data.get('event_count'),
                'allow_conversation_history': request.data.get('allow_conversation_history', 'false').lower() == 'true',
                'accept_lgpd': request.data.get('accept_lgpd', 'false').lower() == 'true'
            }

            logger.info(f"Dados preparados para serialização: {data}")

            validation_result = self.validate_with_ai(files, data)
            if not validation_result.get("valid", False):
                logger.error(f"Falha na validação por IA: {validation_result.get('validation_details', 'Erro desconhecido')}")
                return Response(
                    {"error": validation_result.get("validation_details", "Falha na validação dos documentos")},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            
            instance = serializer.save()
            self.calculate_initial_score(instance)

            dynamic_description = self.generate_fan_description(instance)
            instance.fan_description = dynamic_description
            instance.save()

            for file in files:
                logger.info(f"Arquivo processado: {file.name}")

            return Response({
                "success": True,
                "data": QuizEntrySerializer(instance).data,
                "fan_level": instance.fan_level,
                "fan_score": instance.fan_score,
                "fan_description": dynamic_description
            }, status=status.HTTP_201_CREATED)

        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {str(e)}")
            return Response(
                {"error": "Formato inválido para links sociais"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Erro inesperado ao processar POST: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Erro ao processar sua solicitação: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def generate_fan_description(self, instance):
        try:
            user_data = {
                'full_name': instance.full_name,
                'event_count': instance.event_count,
                'buy_details': instance.buy_details,
                'has_twitter': hasattr(instance.user, 'twitter_account')
            }

            prompt = f"""
            Crie uma descrição criativa para um torcedor nível {instance.fan_level} com estes dados:
            - Nome: {user_data['full_name']}
            - Eventos participados: {user_data['event_count']}
            - Produtos comprados: {user_data['buy_details']}
            - Twitter vinculado: {'Sim' if user_data['has_twitter'] else 'Não'}

            Regras:
            1. Use no máximo 5 frases
            2. Seja criativo e engajador
            3. Adapte ao nível do torcedor
            4. Inclua emojis relevantes
            5. Formato: "Você é [descrição]! [Motivação/curiosidade]"
            """

            headers = {
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "openai/gpt-3.5-turbo",  
                "response_format": {"type": "text"},
                "messages": [
                    {
                        "role": "system",
                        "content": "Você é um especialista em criar descrições criativas para torcedores."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 300
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )
            response.raise_for_status()

            result = response.json()
            description = result['choices'][0]['message']['content'].strip()
            
            instance.fan_description = description
            instance.save()
            
            logger.info(f"Descrição gerada para {instance.user}: {description}")
            return description

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para a IA: {str(e)}")
            fallback = self.get_fallback_description(instance.fan_level)
            instance.fan_description = fallback
            instance.save()
            return fallback
            
        except Exception as e:
            logger.error(f"Erro geral ao gerar descrição: {str(e)}", exc_info=True)
            fallback = self.get_fallback_description(instance.fan_level)
            instance.fan_description = fallback
            instance.save()
            return fallback

        except Exception as e:
            logger.error(f"Erro ao gerar descrição: {str(e)}")
            return self.get_fallback_description(instance.fan_level)

    def get_fallback_description(self, fan_level):
        descriptions = {
            'doido_por_furia': "Você é DOIDO POR FURIA! Um super fã que não perde um evento! 🎉🔥",
            'fanatico': "Você é fanático pela FURIA! Acompanha tudo e participa ativamente! ⚡",
            'big_fan': "Você é um grande fã! Continue acompanhando a FURIA! 👏",
            'regular_fan': "Você é um fã regular, mas pode se envolver mais! 💪",
            'not_fan': "Você está começando sua jornada como fã da FURIA! Bem-vindo! 🎮"
        }
        return descriptions.get(fan_level, "Seu nível de torcedor está sendo avaliado.")

    def extract_text_from_file(self, file):
        try:
            text = ""
            logger.info(f"Processando arquivo: {file.name}, tipo: {file.content_type}")
            
            file.seek(0)
            
            if file.content_type == 'application/pdf':
                try:
                    pdf_content = file.read()
                    if not pdf_content:
                        raise ValueError("Arquivo PDF vazio ou corrompido")
                        
                    images = convert_from_bytes(pdf_content, dpi=200) 
                    for i, img in enumerate(images):
                        logger.info(f"Processando página {i+1} do PDF")
                        try:
                            text += pytesseract.image_to_string(img, lang="por")
                        except Exception as ocr_error:
                            logger.error(f"Erro OCR na página {i+1}: {str(ocr_error)}")
                            raise ValueError(f"Erro ao ler texto da página {i+1}")
                except Exception as pdf_error:
                    logger.error(f"Erro ao processar PDF: {str(pdf_error)}", exc_info=True)
                    raise ValueError("Erro ao processar o arquivo PDF - verifique se é um PDF válido")
            else:
                try:
                    file.seek(0)  
                    image = Image.open(file)
                    text = pytesseract.image_to_string(image, lang="por")
                except Exception as img_error:
                    logger.error(f"Erro ao processar imagem: {str(img_error)}", exc_info=True)
                    raise ValueError("Erro ao processar o arquivo de imagem - formato não suportado ou corrompido")
            
            logger.info(f"Texto extraído (primeiros 100 chars): {text[:100]}...")
            return text.strip() 
        except Exception as e:
            logger.error(f"Erro ao extrair texto: {str(e)}", exc_info=True)
            raise

    def validate_with_ai(self, files, data):
        try:
            extracted_texts = []
            for f in files:
                try:
                    text = self.extract_text_from_file(f)
                    extracted_texts.append(text)
                except Exception as e:
                    logger.error(f"Erro ao processar arquivo {f.name}: {str(e)}")
                    return {
                        "valid": False,
                        "validation_details": f"Erro ao processar documento: {f.name}"
                    }

            combined_text = "\n".join(extracted_texts)
            
            analysis_data = {
                "form_data": {
                    "nome": (data.get('full_name') or '').strip(),
                    "cpf": (data.get('cpf') or '').strip(),
                    "rg": (data.get('rg') or '').strip(),
                    "eventos_comparecidos": int(data.get('event_count', 0)),
                    "compras_realizadas": int(data.get('buy_details', 0))
                },
                "documentos_texto": combined_text[:2000]  # Limita o tamanho
            }

            prompt = f"""
            Você é um validador de documentos oficiais. Analise os dados abaixo e retorne um JSON com:
            - "valid": boolean (True apenas se os documentos são documentos oficiais válidos E as informações batem)
            - "validation_details": string (explicação detalhada da validação)
            - "document_type": string (tipo de documento identificado)

            DADOS PARA ANÁLISE:
            {json.dumps(analysis_data, indent=2)}

            REGRAS ESTRITAS:
            1. O texto deve ser claramente de um documento oficial (RG, CPF, CNH, comprovante, etc.)
            2. Deve conter pelo menos 3 informações que batam com os dados cadastrais
            3. CPF/RG devem ser legíveis e corresponder aos dados do formulário
            4. Nome completo deve aparecer claramente e corresponder
            5. Se o texto for de um tipo de documento não relevante (como currículo, carta, etc.), considere como inválido

            FORMATO DE RESPOSTA ESPERADO:
            {{
                "valid": boolean,
                "validation_details": string,
                "document_type": string,
                "matches": {{
                    "nome": boolean,
                    "cpf": boolean,
                    "rg": boolean
                }}
            }}
            """

            headers = {
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "openai/gpt-3.5-turbo",
                "response_format": {"type": "json_object"},
                "messages": [
                    {
                        "role": "system",
                        "content": "Você é um especialista rigoroso em validação de documentos oficiais. Rejeite qualquer documento que não seja claramente um documento oficial válido."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "temperature": 0.1,  
                "max_tokens": 1000
            }

            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                
                ai_response = response.json()
                message_content = ai_response['choices'][0]['message']['content']
                
                try:
                    validation_data = json.loads(message_content)
                    
                    document_type = validation_data.get("document_type", "").lower()
                    
                    
                
                    
                    return {
                        "valid": validation_data.get("valid", False),
                        "validation_details": validation_data.get("validation_details", "Validação falhou sem detalhes"),
                        "matches": validation_data.get("matches", {})
                    }

                except json.JSONDecodeError:
                    logger.error("Resposta da IA não é JSON válido")
                    return {
                        "valid": False,
                        "validation_details": "Erro técnico na validação"
                    }

            except requests.exceptions.RequestException as e:
                logger.error(f"Erro na requisição para a IA: {str(e)}")
                return {
                    "valid": False,
                    "validation_details": "Serviço de validação indisponível"
                }

        except Exception as e:
            logger.error(f"Erro geral na validação por IA: {str(e)}", exc_info=True)
            return {
                "valid": False,
                "validation_details": "Erro interno na validação"
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
                    'fan_score': entry.fan_score,
                    'fan_description': entry.fan_description
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
    
    def perform_update(self, serializer):
        instance = serializer.save()
        self.recalculate_fan_score(instance)
        self.generate_fan_description(instance)

    def recalculate_fan_score(self, instance):
        twitter_data = {}
        if hasattr(self.request.user, 'twitter_account'):
            twitter_data = self.request.user.twitter_account.extra_data
        
        chat_message_count = 0
        try:
            from chat.models import Message
            chat_message_count = Message.objects.filter(
                Q(chat__user=self.request.user) | Q(chat__user__isnull=True),
                role='user'
            ).count()
        except Exception as e:
            logger.error(f"Erro ao contar mensagens: {str(e)}")

        quiz_data = {
            'event_count': instance.event_count,
            'buy': instance.buy,
            'buy_details': instance.buy_details,
            'attended_event': 'yes' if instance.event_count and instance.event_count > 0 else 'no'
        }


        fan_level, fan_score = evaluate_fan_level(
            quiz_data,
            twitter_data,
            chat_message_count,
            instance.allow_conversation_history
        )
        
        logger.info(f"Novo nível: {fan_level}, score: {fan_score}")
        
        instance.fan_level = fan_level
        instance.fan_score = fan_score
        instance.save()

    def generate_fan_description(self, instance):
        try:
            from .views import QuizEntryCreateView
            create_view = QuizEntryCreateView()
            description = create_view.generate_fan_description(instance)
            instance.fan_description = description
            instance.save()
            return description
        except Exception as e:
            logger.error(f"Erro ao atualizar descrição do fã: {str(e)}")
            fallback = self.get_fallback_description(instance.fan_level)
            instance.fan_description = fallback
            instance.save()
            return fallback

    def get_fallback_description(self, fan_level):
        descriptions = {
            'doido_por_furia': "Você é DOIDO POR FURIA! Um super fã que não perde um evento! 🎉🔥",
            'fanatico': "Você é fanático pela FURIA! Acompanha tudo e participa ativamente! ⚡",
            'big_fan': "Você é um grande fã! Continue acompanhando a FURIA! 👏",
            'regular_fan': "Você é um fã regular, mas pode se envolver mais! 💪",
            'not_fan': "Você está começando sua jornada como fã da FURIA! Bem-vindo! 🎮"
        }
        return descriptions.get(fan_level, "Seu nível de torcedor está sendo avaliado.")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_twitter_validation(request):
    try:
        twitter_account = TwitterLinkedAccount.objects.get(user=request.user)
        
        if not twitter_account.fetch_twitter_data(force_refresh=True):
            return Response({'error': 'Falha ao atualizar Twitter'}, status=400)
        
        quiz_entry = QuizEntry.objects.get(user=request.user)
        
        twitter_data = twitter_account.extra_data
        
        has_interaction = twitter_data.get('interactions_count', 0) > 0
        
        fan_level, fan_score = evaluate_fan_level(
            quiz_data={
                'event_count': quiz_entry.event_count or 0,
                'buy': (quiz_entry.buy or '').strip().lower(),
                'buy_details': (quiz_entry.buy_details or '').strip().lower()
            },
            twitter_data={
                'interactions_count': 1 if has_interaction else 0
            },
        )

        
        quiz_entry.fan_level = fan_level
        quiz_entry.fan_score = fan_score
        quiz_entry.save()
        
        return Response({
            'success': True,
            'new_level': fan_level,
            'new_score': fan_score,
            'has_twitter_interaction': has_interaction,
            'last_updated': twitter_data.get('last_updated')
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
        logger.error(f"Erro no refresh Twitter: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Erro interno no servidor'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class FanCardView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FanCardSerializer

    def get_object(self):
        fan_card, created = FanCard.objects.get_or_create(user=self.request.user)
        return fan_card

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        if data.get('photo'):
            data['photo'] = request.build_absolute_uri(data['photo'])

        return Response(data)

    def perform_update(self, serializer):
        instance = self.get_object()
        
        if 'photo' in self.request.FILES and instance.photo:
            old_photo_path = instance.photo.path
            if os.path.exists(old_photo_path):
                os.remove(old_photo_path)
        
        serializer.save()
