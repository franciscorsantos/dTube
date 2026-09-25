from pydantic import BaseModel, Field
from typing import List, Optional


class VideoFormatInfo(BaseModel):
    format_id: str = Field(..., description="ID identificador do formato no yt-dlp")
    extension: str = Field(..., description="Extensão do arquivo (ex: mp4, m4a, webm)")
    resolution: Optional[str] = Field(None, description="Resolução visual (ex: 1080p, 720p) ou nota do formato")
    filesize_bytes: Optional[int] = Field(None, description="Tamanho estimado em bytes")
    filesize_mb: Optional[float] = Field(None, description="Tamanho estimado em Megabytes (MB)")
    note: Optional[str] = Field(None, description="Informações adicionais do formato")
    has_video: bool = Field(..., description="Indica se o formato possui faixa de vídeo")
    has_audio: bool = Field(..., description="Indica se o formato possui faixa de áudio")


class VideoMetadataResponse(BaseModel):
    id: str = Field(..., description="ID único do vídeo no YouTube")
    url: str = Field(..., description="URL original do vídeo")
    title: str = Field(..., description="Título do vídeo")
    channel: str = Field(..., description="Nome do canal ou autor")
    duration_seconds: int = Field(..., description="Duração total em segundos")
    duration_formatted: str = Field(..., description="Duração formatada (HH:MM:SS)")
    thumbnail: Optional[str] = Field(None, description="URL da imagem de capa / thumbnail")
    description: Optional[str] = Field(None, description="Descrição resumida do vídeo")
    formats: List[VideoFormatInfo] = Field(..., description="Lista de formatos disponíveis para download")


class DownloadRequest(BaseModel):
    url: str = Field(
        ...,
        description="URL do vídeo do YouTube",
        examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]
    )
    format: str = Field(
        default="mp4",
        description="Formato de saída desejado: 'mp4' (vídeo) ou 'mp3' (apenas áudio)",
        examples=["mp4", "mp3"]
    )
    quality: Optional[str] = Field(
        default="best",
        description="Qualidade desejada: 'best', '1080p', '720p', '480p' ou 'bestaudio'",
        examples=["best", "1080p", "720p"]
    )


class HTTPErrorDetail(BaseModel):
    detail: str = Field(..., description="Mensagem detalhada do erro")
