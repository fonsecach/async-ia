import json
import logging
import re

from fastapi import HTTPException

from core.config import settings
from models.schemas import OutputFormat

logger = logging.getLogger(__name__)


class AIService:
    """Servico responsavel pela comunicacao da API de IA"""

    def __init__(self):
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        try:
            from openai import AsyncOpenAI

            if not settings.base_url or not settings.api_key:
                raise ValueError('BASE_URL e API_KEY devem ser configurados.')

            self.client = AsyncOpenAI(
                base_url=settings.base_url,
                api_key=settings.api_key,
                timeout=settings.ai_timeout,
            )

            logger.info('Cliente OpenAI inicializado com sucesso.')
        except ImportError as e:
            logger.error(f'Erro ao importar biblioteca OpenAI: {e}')
        except Exception as e:
            logger.error(f'Erro ao inicializar cliente OpenAI: {e}')
            raise ValueError(
                'Erro ao inicializar cliente OpenAI. Verifique as configurações.'
            )

    async def generate_completion(
        self,
        prompt: str,
        file_content: str = '',
        output_format: OutputFormat = OutputFormat.TEXT,
    ) -> str | dict:
        """
        Gera completion usando a API de IA

        Args:
            prompt: Prompt do usuário
            file_content: Conteúdo dos arquivos (opcional)
            output_format: Formato de saída desejado

        Returns:
            Resposta da IA em formato string ou dict
        """
        if not self.client:
            raise HTTPException(status_code=503, detail='Serviço de IA não disponível.')

        full_prompt = self._build_full_prompt(prompt, file_content, output_format)

        try:
            response = await self.client.chat.completions.create(
                model=settings.ai_model,
                messages=[{'role': 'user', 'content': full_prompt}],
                temperature=settings.ai_temperature,
                max_tokens=settings.ai_max_tokens,
            )

            # Validar se a resposta não é None
            if response is None:
                logger.error('Resposta da API é None')
                raise HTTPException(
                    status_code=500, detail='Resposta inválida da API de IA.'
                )

            # Validar se há choices na resposta
            if not hasattr(response, 'choices') or not response.choices:
                logger.error(f'Resposta sem choices: {response}')
                raise HTTPException(
                    status_code=500, detail='Resposta da API não contém choices.'
                )

            # Validar se a primeira choice tem message
            if not hasattr(response.choices[0], 'message') or not response.choices[0].message:
                logger.error(f'Choice sem message: {response.choices[0]}')
                raise HTTPException(
                    status_code=500, detail='Resposta da API não contém message.'
                )

            content = response.choices[0].message.content

            # Validar se o content não é None
            if content is None:
                logger.error('Content da resposta é None')
                raise HTTPException(
                    status_code=500, detail='Conteúdo da resposta é vazio.'
                )

            if output_format == OutputFormat.JSON:
                return self._parse_json_response(content)
            else:
                return content
        except HTTPException:
            # Re-raise HTTPException sem alterar
            raise
        except Exception as e:
            logger.error(f'Erro ao gerar completion: {e}')
            raise HTTPException(
                status_code=500, detail='Erro ao processar solicitação de IA.'
            )

    def _build_full_prompt(
        self, prompt: str, file_content: str, output_format: OutputFormat
    ) -> str:
        full_prompt = prompt

        if file_content:
            full_prompt += f'\n\nConteúdo do arquivo:\n{file_content}'

        if output_format == OutputFormat.JSON:
            full_prompt += """\n\nIMPORTANTE: Responda apenas com um JSON válido,
            sem texto adicional antes ou depois do JSON."""

        return full_prompt

    def _parse_json_response(self, content: str) -> dict:
        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            json_pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|\{[^{}]*\})*\}))*\}'
            json_match = re.search(json_pattern, content, re.DOTALL)

            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

            # Se não conseguir extrair JSON válido, retornar como texto estruturado
            logger.warning('Não foi possível extrair JSON válido da resposta da IA')
            return {
                'response': content.strip(),
                'note': 'Não foi possível extrair JSON válido da resposta.',
            }
