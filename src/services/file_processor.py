import asyncio
import logging
import os
import tempfile
from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile

from core.config import settings

logger = logging.getLogger(__name__)


class FileProcessorService:
    """Serviço para processar arquivos enviados"""

    def __init__(self):
        self.max_file_size = settings.max_file_size_bytes
        self.allowed_extensions = settings.allowed_extensions

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

    def _validate_file(self, file: UploadFile) -> None:
        """Valida o arquivo enviado"""

        if not file.filename:
            raise HTTPException(
                status_code=400, detail='Nome do arquivo não pode ser vazio.'
            )

        file_extension = Path(file.filename).suffix.lower().lstrip('.')
        if file_extension not in self.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f'Tipo de arquivo não permitido: {file_extension}. ',
            )

    async def _process_single_file(self, file: UploadFile) -> tuple[str, str]:
        """Processa um único arquivo"""

        try:
            # Criar arquivo temporário
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=Path(file.filename).suffix
            ) as temp_file:
                temp_path = temp_file.name

            # valida o tamanho do arquivo
            content = await file.read()
            if len(content) > self.max_file_size:
                raise HTTPException(
                    status_code=400,
                    detail='Tamanho do arquivo excede o limite permitido.',
                )

            # escrever o conteudo para o arquivo temporario
            async with aiofiles.open(temp_path, 'wb') as f:
                await f.write(content)

            # Ler conteúdo como texto
            async with aiofiles.open(
                temp_path, encoding='utf-8', errors='ignore'
            ) as f:
                file_content = await f.read()

            return file.filename, file_content

        except Exception as e:
            logger.error(f'Erro ao processar o arquivo {file.filename}: {e}')
            raise HTTPException(
                status_code=500, detail='Erro interno ao processar o arquivo.'
            )
        finally:
            # Remover os arquivos temporarios
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except OSError as e:
                    logger.warning(
                        f'Erro ao remover arquivo temporário {temp_path}: {e}'
                    )
