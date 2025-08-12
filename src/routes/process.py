import logging
import time
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from core.dependencies import get_ai_service, get_file_processor
from models.schemas import (
    ErrorResponse,
    HealthResponse,
    OutputFormat,
    PromptRequest,
    PromptResponse,
)
from services.ai_service import AIService
from services.file_processor import FileProcessorService

logger = logging.getLogger(__name__)

# Router principal
router = APIRouter()


@router.post(
    '/process',
    response_model=PromptResponse,
    responses={
        400: {'model': ErrorResponse, 'description': 'Erro de validação'},
        500: {'model': ErrorResponse, 'description': 'Erro interno do servidor'},
    },
    summary='Processa prompt com arquivos opcionais',
    description='''Endpoint para processamento assíncrono de prompts
    com suporte a múltiplos arquivos e diferentes formatos de saída'''
    ,
)
async def process_prompt(
    prompt: str = Form(..., description='O prompt para processamento'),
    output_format: OutputFormat = Form(
        default=OutputFormat.TEXT, description='Formato de saída (json ou text)'
    ),
    files: list[UploadFile] | None = File(
        default=None, description='Lista opcional de arquivos'
    ),
    ai_service: AIService = Depends(get_ai_service),
    file_processor: FileProcessorService = Depends(get_file_processor),
):

    """Processa um prompt com arquivos opcionais de forma assíncrona.

    **Parâmetros:**
    - **prompt**: Texto do prompt (obrigatório, 1-10000 caracteres)
    - **output_format**: Formato da resposta - 'json' ou 'text' (padrão: text)
    - **files**: Lista opcional de arquivos para contexto (max 10MB cada)

    **Arquivos suportados:**
    - .txt, .csv, .json, .md, .py, .js, .ts, .html, .xml

    **Retorna:**
    - Resposta da IA no formato solicitado
    - Lista de arquivos processados
    - Tempo de processamento
    """

    start_time = time.time()

    try:
        # Validar entrada usando Pydantic
        request_data = PromptRequest(prompt=prompt, output_format=output_format)

        # Processar arquivos de forma assíncrona (se fornecidos)
        files_list = files if files else []
        processed_files, file_content = await file_processor.process_files(files_list)

        logger.info(f'Processando prompt com {len(processed_files)} arquivos')

        # Gerar completion de forma assíncrona
        result = await ai_service.generate_completion(
            request_data.prompt, file_content, request_data.output_format
        )

        processing_time = time.time() - start_time

        logger.info(f'Processamento concluído em {processing_time:.2f}s')

        return PromptResponse(
            success=True,
            data=result,
            files_processed=processed_files,
            processing_time_seconds=round(processing_time, 2),
            message='Processamento concluído com sucesso',
        )

    except HTTPException:
        # Re-raise HTTP exceptions (já tratadas nos serviços)
        raise
    except Exception as e:
        error_msg = f'Erro inesperado durante o processamento: {str(e)}'
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@router.get(
    '/health',
    response_model=HealthResponse,
    summary='Health check da aplicação',
    description='Verifica se a aplicação está funcionando corretamente',
)
async def health_check():
    """Endpoint de health check para monitoramento da aplicação"""
    return HealthResponse(
        status='healthy',
        service='async-ai-processing',
        timestamp=datetime.utcnow().isoformat(),
    )


@router.get(
    '/',
    summary='Informações da API',
    description='Endpoint raiz com informações básicas da API',
)
async def root():
    """Endpoint raiz com informações da API"""
    return {
        'message': 'Async AI Processing Service',
        'version': '1.0.0'
    }
