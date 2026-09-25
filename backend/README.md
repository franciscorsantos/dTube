# YouTube Downloader & Audio Extractor API 🚀

API RESTful assíncrona de alta performance desenvolvida em **Python 3.10+** com **FastAPI** e **yt-dlp** para extração de metadados e download de vídeos e áudios do YouTube.

---

## 📋 Arquitetura do Projeto

O projeto foi estruturado seguindo os princípios de modularidade, separação de responsabilidades (SoC), execução assíncrona com `asyncio.to_thread` para não bloquear a event loop do FastAPI e limpeza automática de recursos em segundo plano via `BackgroundTask`.

```text
down_youtube/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Ponto de entrada da aplicação FastAPI e Uvicorn
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py            # Endpoints (GET /api/info e POST /api/download)
│   │   └── schemas.py           # Modelos Pydantic V2 de requisição e resposta
│   ├── services/
│   │   ├── __init__.py
│   │   └── youtube_service.py   # Camada de negócio, integração yt-dlp e suporte a cookies
│   └── utils/
│       ├── __init__.py
│       └── helpers.py           # Utilitários (validação de URL, conversão de tempo, limpeza)
├── tests/
│   └── test_api.py              # Suíte de testes automatizados com pytest
├── cookies.txt                  # Arquivo opcional contendo cookies Netscape para bypass anti-bot
├── pytest.ini                   # Configurações do ambiente de testes
├── requirements.txt             # Lista de dependências do projeto
└── README.md                    # Instruções completas de uso e solução de problemas
```

---

## 🛡️ Solução para Bloqueio Anti-Bot do YouTube (`Sign in to confirm you're not a bot`)

O YouTube frequentemente exige verificação humana / cookies de sessão para certas conexões ou IPs de servidores.

### Como Resolver:

1. **Exportar Cookies em formato Netscape**:
   - Instale a extensão no seu navegador (Chrome/Edge/Firefox): **"Get cookies.txt LOCALLY"**.
   - Acesse o site do [YouTube](https://www.youtube.com) estando logado na sua conta.
   - Abra a extensão e clique em **Export** para baixar o arquivo `cookies.txt`.

2. **Adicionar o arquivo ao Backend**:
   - Salve o arquivo com o nome **`cookies.txt`** na raiz do projeto `down_youtube/`.
   - O serviço detectará automaticamente o arquivo e passará as credenciais de sessão para o `yt-dlp`.

3. **(Opcional) Definir caminho personalizado via variável de ambiente**:
   ```bash
   YOUTUBE_COOKIE_FILE=/caminho/para/meus_cookies.txt
   ```

---

## ✨ Funcionalidades

### 1. `GET /api/info`
- **Descrição**: Recebe uma URL do YouTube via query parameter e retorna metadados completos do vídeo em JSON.
- **Campos retornados**: Título, Canal/Autor, Duração em segundos e formatada (`HH:MM:SS`), Thumbnail, Descrição e lista com todos os formatos/resoluções disponíveis.

### 2. `POST /api/download`
- **Descrição**: Recebe uma URL e o formato desejado (`mp4` ou `mp3`). Realiza o download/conversão no servidor temporariamente e envia o arquivo via `FileResponse`.
- **Limpeza Automática de Disco**: O diretório temporário criado para a requisição é **removido automaticamente** assim que o envio do arquivo ao cliente é concluído (`BackgroundTask`).

---

## 🛠️ Requisitos de Ambiente

- **Python 3.10 ou superior**
- **FFmpeg** (Recomendado para extração de MP3 e mesclagem de vídeo/áudio em 1080p+).

### Instalando o FFmpeg:

- **Windows**:
  ```powershell
  winget install ffmpeg
  ```
- **Ubuntu/Debian**:
  ```bash
  sudo apt update && sudo apt install -y ffmpeg
  ```
- **macOS**:
  ```bash
  brew install ffmpeg
  ```

---

## 🚀 Como Executar o Projeto

### 1. Clonar o repositório e entrar na pasta:
```bash
cd down_youtube
```

### 2. Criar e ativar o ambiente virtual (venv):

- **Linux / macOS**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- **Windows (PowerShell)**:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```

### 3. Instalar as dependências:
```bash
pip install -r requirements.txt
```

### 4. Iniciar o servidor Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧪 Executando os Testes

```bash
pytest
```
