/**
 * Configuração central da aplicação Frontend
 */
const CONFIG = {
  // URL base da API de download do YouTube
  API_BASE_URL: window.ENV_API_URL || "http://localhost:8000/api",
  
  // Timeout padrão para requisições em milissegundos
  TIMEOUT_MS: 300000, // 5 minutos para vídeos maiores
  
  // Nomes e tipos de arquivo suportados
  FORMATS: {
    mp4: {
      extension: "mp4",
      mimeType: "video/mp4",
      label: "Vídeo (MP4)"
    },
    mp3: {
      extension: "mp3",
      mimeType: "audio/mpeg",
      label: "Áudio (MP3)"
    }
  }
};

window.CONFIG = CONFIG;
