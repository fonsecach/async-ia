from enum import Enum

from pydantic import BaseModel, Field, field_validator


class OutputFormat(int, Enum):
    """Enum para formatos de saída suportados"""

    JSON = 1
    TEXT = 2

    @property
    def name(self) -> str:
        names = {1: 'json', 2: 'text'}
        return names[self.value]


class PromptRequest(BaseModel):
    """Modelo para requisicao de processamento de prompt"""

    prompt: str = Field(..., min_length=1, max_length=2000)
    output_format: OutputFormat = Field(default=OutputFormat.TEXT)

    @field_validator('prompt')
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError('O Prompt não pode estar vazio')
        return v.strip()


class PromptResponse(BaseModel):
    """Modelo para resposta do processamento"""

    success: bool
    data: str | dict
    files_processed: list[str]
    processing_time_seconds: float
    message: str | None = None


class ErrorResponse(BaseModel):
    """Modelo para resposta de erro"""

    success: bool = False
    error: str
    details: str | None = None


class HealthResponse(BaseModel):
    """Modelo para resposta de verificação de saúde"""

    success: bool = True
    message: str = 'O sistema está saudável'
    timestamp: str
