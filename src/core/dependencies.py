from functools import lru_cache

from services.ai_service import AIService
from services.file_processor import FileProcessorService


@lru_cache
def get_ai_service() -> AIService:
    """
    Dependência singleton para injeção do serviço de IA
    Usa LRU cache para garantir uma única instância
    """
    return AIService()


@lru_cache
def get_file_processor() -> FileProcessorService:
    """
    Dependência singleton para injeção do processador de arquivos
    Usa LRU cache para garantir uma única instância
    """
    return FileProcessorService()
