import asyncio
import logging
import os
import tempfile
from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile

from core.config import settings

logger = logging.getLogger(__name__)


class FileProcessosrService:
    """Serviço para processar arquivos enviados"""

    def __init__(self):
        self.max_file_size = settings.max_file_size_bytes
        self.allowed_file_types = settings.allowed_file_types

    async def process_files(self, files: list[UploadFile]) -> tuple[list[str], str]:
        """
        Processa uma lista de arquivos de forma assíncrona

        Args:
            files: Lista de arquivos enviados

        Returns:
            Tupla contendo (lista_nomes_arquivos, conteudo_combinado)
        """

        if not files:
            return [], ''

        # validar os arquivos antes do processamento
        for file in files:
            self._validate_file(file)

        # processar os arquivos com asyncio.gather
        tasks = [self._process_single_file(file) for file in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed_files = []
        combined_content = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_msg = (
                    f'Erro ao processar o arquivo {files[i].filename}: : {result}'
                )
                logger.error(error_msg)
                raise HTTPException(status_code=400, detail=error_msg)

            filename, content = result
            processed_files.append(filename)
            combined_content.append(content)

        return processed_files, '\n'.join(combined_content)
