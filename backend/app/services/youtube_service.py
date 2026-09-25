import os
import shutil
import tempfile
import asyncio
import logging
from typing import Dict, Any, Tuple
import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError
from fastapi import HTTPException, status

from app.utils.helpers import is_valid_youtube_url, format_duration

logger = logging.getLogger("youtube_downloader.service")


class YouTubeService:
    """
    Serviço assíncrono para abstração do yt-dlp, suporte a cookies anti-bot e tratamento de erros.
    """

    @staticmethod
    def _get_base_ydl_opts() -> Dict[str, Any]:
        """
        Retorna as opções base do yt-dlp, incluindo cookies (cookies.txt) e parâmetros anti-bot.
        """
        opts: Dict[str, Any] = {
            'quiet': True,
            'no_warnings': True,
            # Configuração de clientes alternativos para minimizar bloqueios anti-bot do YouTube
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios', 'web', 'mweb']
                }
            }
        }

        # 1. Verificar arquivo de cookies (cookies.txt)
        cookie_file = os.getenv("YOUTUBE_COOKIE_FILE", "cookies.txt")
        if os.path.exists(cookie_file):
            opts['cookiefile'] = cookie_file
            logger.info(f"Carregando cookies a partir do arquivo: {cookie_file}")

        # 2. Verificar suporte a Proxy
        proxy = os.getenv("YOUTUBE_PROXY")
        if proxy:
            opts['proxy'] = proxy

        return opts

    @classmethod
    def _extract_info_sync(cls, url: str) -> Dict[str, Any]:
        ydl_opts = cls._get_base_ydl_opts()
        ydl_opts.update({
            'extract_flat': False,
            'skip_download': True,
        })
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise ExtractorError("Não foi possível extrair dados do vídeo.")
            return info

    @classmethod
    async def get_info(cls, url: str) -> Dict[str, Any]:
        if not is_valid_youtube_url(url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL inválida ou formato de link do YouTube não suportado."
            )

        try:
            info = await asyncio.to_thread(cls._extract_info_sync, url)
        except DownloadError as e:
            err_msg = str(e)
            if "Sign in to confirm you" in err_msg or "not a bot" in err_msg:
                detail = (
                    "O YouTube bloqueou o acesso exigindo verificação anti-bot. "
                    "Para corrigir, exporte os cookies do seu navegador para um arquivo 'cookies.txt' "
                    "na raiz do projeto backend."
                )
            elif "Private video" in err_msg:
                detail = "O vídeo solicitado é privado."
            elif "Sign in to confirm your age" in err_msg:
                detail = "O vídeo possui restrição de idade no YouTube."
            elif "Video unavailable" in err_msg:
                detail = "Vídeo indisponível ou removido do YouTube."
            else:
                detail = f"Erro no serviço do YouTube: {err_msg}"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
        except ExtractorError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar metadados do vídeo: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao processar os metadados do vídeo."
            )

        formats_list = []
        raw_formats = info.get('formats', [])
        for f in raw_formats:
            vcodec = f.get('vcodec', 'none')
            acodec = f.get('acodec', 'none')
            has_v = vcodec != 'none' and vcodec is not None
            has_a = acodec != 'none' and acodec is not None

            filesize = f.get('filesize') or f.get('filesize_approx')
            filesize_mb = round(filesize / (1024 * 1024), 2) if filesize else None

            res = f.get('resolution')
            if not res and f.get('height'):
                res = f"{f.get('height')}p"
            elif not res:
                res = f.get('format_note', 'N/A')

            formats_list.append({
                "format_id": str(f.get("format_id", "")),
                "extension": f.get("ext", ""),
                "resolution": res,
                "filesize_bytes": filesize,
                "filesize_mb": filesize_mb,
                "note": f.get("format_note"),
                "has_video": has_v,
                "has_audio": has_a,
            })

        duration = info.get('duration', 0) or 0

        return {
            "id": info.get("id", ""),
            "url": url,
            "title": info.get("title", "Sem título"),
            "channel": info.get("uploader") or info.get("channel") or "Canal desconhecido",
            "duration_seconds": duration,
            "duration_formatted": format_duration(duration),
            "thumbnail": info.get("thumbnail"),
            "description": info.get("description"),
            "formats": formats_list
        }

    @classmethod
    def _download_sync(cls, url: str, format_type: str, quality: str, temp_dir: str) -> str:
        out_tmpl = os.path.join(temp_dir, "%(title)s.%(ext)s")
        format_type_clean = format_type.strip().lower()

        ydl_opts = cls._get_base_ydl_opts()
        ydl_opts.update({
            'outtmpl': out_tmpl,
            'restrictfilenames': False,
        })

        if format_type_clean in ["mp3", "audio"]:
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            if quality and quality != "best":
                if quality.endswith("p") and quality[:-1].isdigit():
                    height = quality[:-1]
                    format_str = f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={height}][ext=mp4]/best[height<={height}]/best"
                else:
                    format_str = f"{quality}[ext=mp4]/best[ext=mp4]/best"
            else:
                format_str = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"

            ydl_opts.update({'format': format_str})

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        downloaded_files = os.listdir(temp_dir)
        if not downloaded_files:
            raise ExtractorError("Falha ao salvar o arquivo no diretório temporário.")

        return os.path.join(temp_dir, downloaded_files[0])

    @classmethod
    async def download(cls, url: str, format_type: str = "mp4", quality: str = "best") -> Tuple[str, str, str]:
        if not is_valid_youtube_url(url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL inválida ou formato de link do YouTube não suportado."
            )

        temp_dir = tempfile.mkdtemp(prefix="ytdl_")

        try:
            file_path = await asyncio.to_thread(
                cls._download_sync, url, format_type, quality, temp_dir
            )
            filename = os.path.basename(file_path)
            return file_path, filename, temp_dir
        except DownloadError as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            err_msg = str(e)
            if "Sign in to confirm you" in err_msg or "not a bot" in err_msg:
                detail = (
                    "O YouTube bloqueou o acesso exigindo verificação anti-bot. "
                    "Para corrigir, adicione um arquivo 'cookies.txt' válido na raiz do projeto."
                )
            elif "ffmpeg" in err_msg.lower() or "ffprobe" in err_msg.lower():
                detail = "O download/conversão para este formato requer o binário FFmpeg instalado no servidor."
            elif "Private video" in err_msg:
                detail = "O vídeo solicitado é privado."
            elif "Sign in to confirm your age" in err_msg:
                detail = "O vídeo possui restrição de idade no YouTube."
            else:
                detail = f"Erro ao realizar o download via yt-dlp: {err_msg}"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            logger.error(f"Erro inesperado no processo de download: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Falha interna no servidor durante o download: {str(e)}"
            )
