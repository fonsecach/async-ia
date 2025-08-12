import logging
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.dependencies import get_ai_service
from routes.process import router

# Configuração de logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciamento do ciclo de vida da aplicação"""
    logger.info('🚀 Iniciando Async AI Processing Service...')

    try:
        # Inicializar serviços críticos
        ai_service = get_ai_service()
        logger.info('✅ Serviços inicializados com sucesso')

        # Validar configurações essenciais
        if not settings.base_url or not settings.api_key:
            raise ValueError('❌ BASE_URL e API_KEY devem estar configurados')

        logger.info(f'🔧 Configurações carregadas - Model: {settings.ai_model}')
        logger.info(f'📁 Max file size: {settings.max_file_size_mb}MB')
        logger.info(f'📋 Allowed extensions: {", ".join(settings.allowed_extensions)}')

    except Exception as e:
        logger.error(f'❌ Erro ao inicializar serviços: {e}')
        raise

    yield

    logger.info('🛑 Finalizando Async AI Processing Service...')


# Criar aplicação FastAPI
app = FastAPI(
    title='Async AI Processing Service',
    description=(
        'Serviço assíncrono para processamento de prompts com suporte a arquivos múltiplos. '
        'Utiliza processamento concorrente para otimizar performance e oferece saída em '
        'diferentes formatos (JSON/TEXT).'
    ),
    version='1.0.0',
    lifespan=lifespan,
    docs_url='/docs',
    redoc_url='/redoc',
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['GET', 'POST'],
    allow_headers=['*'],
)

# Incluir rotas
app.include_router(router, prefix='', tags=['API'])


# Middleware de logging (opcional)
@app.middleware('http')
async def log_requests(request, call_next):
    """Middleware para log de requisições"""
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f'{request.method} {request.url.path} - '
        f'Status: {response.status_code} - '
        f'Time: {process_time:.3f}s'
    )

    return response


if __name__ == '__main__':
    logger.info(f'🌐 Iniciando servidor em http://{settings.host}:{settings.port}')

    uvicorn.run(
        'main:app',
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level,
    )
