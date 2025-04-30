import json
import logging
import requests
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.conf import settings
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
from .models import QuizEntry
from .serializers import QuizEntrySerializer

logger = logging.getLogger(__name__)

class QuizEntryCreateView(generics.CreateAPIView):
    queryset = QuizEntry.objects.all()
    serializer_class = QuizEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

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

    def validate_with_ai(self, files, data):
        try:
            extracted_texts = [self.extract_text_from_file(f) for f in files]
            combined_text = "\n".join(extracted_texts)
            
            logger.info(f"Dados para validação: {data}")
            logger.debug(f"Texto combinado dos documentos (início): {combined_text[:500]}...")

            prompt = f"""
            ANALISE DE DOCUMENTOS - SISTEMA DE VALIDAÇÃO

            DADOS INFORMADOS PELO USUÁRIO:
            - Nome completo: {data.get('full_name', 'Não informado')}
            - CPF: {data.get('cpf', 'Não informado')}
            - RG: {data.get('rg', 'Não informado')}

            TEXTO EXTRAÍDO DOS DOCUMENTOS:
            {combined_text}

            INSTRUÇÕES:
            1. Compare cuidadosamente os dados informados com os encontrados nos documentos
            2. Considere possíveis variações de formatação
            3. Para CPF, ignore pontuação e compare apenas os números
            4. Para nome, considere pequenas diferenças (ex: abreviações)
            5. Responda APENAS no formato JSON especificado

            RESPOSTA EM JSON (apenas):
            {{
                "valid": boolean,
                "reason": string,
                "found_data": {{
                    "nome": string,
                    "cpf": string,
                    "rg": string
                }}
            }}
            """

            headers = {
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "HTTP-Referer": "http://localhost:3000",  
                "X-Title": "FURIA Fan Validation",      
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "openai/gpt-3.5-turbo",  
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": "Você é um validador de documentos. Responda APENAS em JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1
            }

            logger.info("Enviando requisição para OpenRouter...")
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            logger.info(f"Resposta da API: Status {response.status_code}, Body: {response.text}")
            
            response.raise_for_status()
            ai_response = response.json()
            
            try:
                message_content = ai_response['choices'][0]['message']['content']
                validation_data = json.loads(message_content)
                
                logger.info(f"Resposta da IA parseada: {validation_data}")
                
                return {
                    "valid": validation_data.get("valid", False),
                    "details": validation_data.get("reason", "Validação não concluída"),
                    "found_data": validation_data.get("found_data", {}),
                    "ai_response": ai_response
                }
                
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Erro ao processar resposta: {str(e)}")
                return {
                    "valid": False,
                    "details": "Erro na validação automática",
                    "error": str(e),
                    "raw_response": ai_response
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para OpenRouter: {str(e)}")
            return {
                "valid": False,
                "details": "Erro de conexão com o serviço de validação",
                "error": str(e)
            }

def check_ai_status(request):
    try:
        response = requests.get("https://api.openai.com/v1/models", headers={
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}"
        }, timeout=5)
        return Response({"status": "operational" if response.ok else "unavailable"})
    except Exception as e:
        return Response({"status": "error", "details": str(e)})