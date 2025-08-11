import os
from typing import set

import dotenv
from pydantic_settings import BaseSettings

dotenv.load_dotenv()


class Settings(BaseSettings):
    """Configurações da aplicação"""

    # API configuration
    base_url: str = os.getenv('BASE_URL')
    api_key: str = os.getenv('API_KEY')

    # File processing configuration
    max_file_size_mb: int = int(os.getenv('MAX_FILE_SIZE_MB', 10))
    allowed_file_types: set[str] = set(os.getenv('ALLOWED_FILE_TYPES').split(','))
    temp_dir: str = os.getenv('TEMP_DIR')

    # API configuration IA
    ai_timeout: float = float(os.getenv('AI_TIMEOUT', 60.0))
    ai_temperature: float = float(os.getenv('AI_TEMPERATURE', 0.6))
    ai_max_tokens: int = int(os.getenv('AI_MAX_TOKENS', 4000))
    ai_model: str = os.getenv('AI_MODEL', 'deepseek-reasoner')


class Config:
    env_file = '.env'
    case_sensitive = False


@property
def max_file_size_bytes(self) -> int:
    return self.max_file_size_mb * 1024 * 1024


settings = Settings()
