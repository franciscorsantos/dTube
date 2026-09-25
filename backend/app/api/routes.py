import mimetypes
import urllib.parse
from fastapi import APIRouter, Query, status
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from app.api.schemas import (
    VideoMetadataResponse,
    DownloadRequest,
    HTTPErrorDetail
)
from app.services.youtube_service import YouTubeService
from app.utils.helpers import cleanup_temp_dir

router = APIRouter(prefix="/api", tags=["YouTube Downloader"])


@router.get(
    "/info",
    response_model=VideoMetadataResponse,
    summary="Obter metadados do vídeo",
    responses={
        400: {"model": HTTPErrorDetail, "description": "URL inválida ou vídeo indisponível"},
        500: {"model": HTTPErrorDetail, "description": "Erro interno no servidor"}
    }
)
async def get_video_info(
    url: str = Query(..., description="URL completa do vídeo do YouTube (ex: https://www.youtube.com/watch?v=...)")
):
    """
    Retorna metadados detalhados de um vídeo do YouTube em formato JSON:
    - **Título**
    - **Canal / Autor**
    - **Duração (segundos e formatada)**
    - **Thumbnail**
    - **Lista completa de resoluções/formatos disponíveis**
    """
    return await YouTubeService.get_info(url)


@router.post(
    "/download",
    summary="Baixar vídeo ou extrair áudio",
    responses={
        200: {
            "content": {"application/octet-stream": {}},
            "description": "Arquivo de vídeo ou áudio pronto para download."
        },
        400: {"model": HTTPErrorDetail, "description": "Parâmetros inválidos ou erro de conversão (ex: FFmpeg ausente)"},
        500: {"model": HTTPErrorDetail, "description": "Erro interno durante o processamento"}
    }
)
async def download_media(request: DownloadRequest):
    """
    Faz o download do vídeo ou extrai o áudio temporariamente no servidor, 
    retornando o arquivo diretamente via stream/FileResponse.
    
    - **format**: 'mp4' (vídeo com áudio) ou 'mp3' (áudio extraído).
    - **quality**: 'best', '1080p', '720p', etc.
    
    *Nota: O arquivo temporário é **excluído automaticamente** do servidor imediatamente após a conclusão do download pelo cliente.*
    """
    file_path, filename, temp_dir = await YouTubeService.download(
        url=request.url,
        format_type=request.format,
        quality=request.quality or "best"
    )

    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        if request.format.lower() in ["mp3", "audio"]:
            mime_type = "audio/mpeg"
        else:
            mime_type = "video/mp4"

    encoded_filename = urllib.parse.quote(filename)

    return FileResponse(
        path=file_path,
        media_type=mime_type,
        filename=filename,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        },
        background=BackgroundTask(cleanup_temp_dir, temp_dir)
    )
