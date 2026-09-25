import re
import os
import shutil
import logging

logger = logging.getLogger("youtube_downloader.helpers")

# Regex para validação de URLs do YouTube (watch, shorts, embed, youtu.be, m.youtube, music.youtube)
YOUTUBE_REGEX = re.compile(
    r'^(https?://)?(www\.|m\.|music\.)?(youtube\.com/(watch\?.*v=|shorts/|embed/)|youtu\.be/)[a-zA-Z0-9_-]{11}'
)


def is_valid_youtube_url(url: str) -> bool:
    """
    Valida se uma URL pertence ao formato esperado do YouTube.
    """
    if not url:
        return False
    return bool(YOUTUBE_REGEX.search(url.strip()))


def format_duration(seconds: float | int | None) -> str:
    """
    Converte a duração em segundos para a formatação HH:MM:SS ou MM:SS.
    """
    if seconds is None or seconds < 0:
        return "N/A"
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def cleanup_temp_dir(dir_path: str) -> None:
    """
    Função de callback executada via BackgroundTask para excluir o diretório temporário
    e o arquivo baixado do servidor assim que a resposta HTTP é enviada ao usuário.
    """
    try:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path, ignore_errors=True)
            logger.info(f"Limpeza concluída: diretório temporário removido -> {dir_path}")
    except Exception as e:
        logger.error(f"Erro ao remover o diretório temporário {dir_path}: {e}")
