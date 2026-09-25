import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router

app = FastAPI(
    title="YouTube Downloader & Audio Extractor API",
    description="API assíncrona de alta performance desenvolvida com FastAPI e yt-dlp para obtenção de metadados e download de vídeos e áudios do YouTube.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração de CORS para permitir acesso de aplicações frontend Web (React, Vue, HTML/JS puro)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro dos endpoints da API
app.include_router(api_router)


@app.get("/", tags=["Health Check"])
async def root():
    return {
        "status": "online",
        "service": "YouTube Downloader API",
        "version": "1.0.0",
        "documentation": "/docs"
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
