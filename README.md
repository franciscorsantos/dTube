# 🎬 dTube — YouTube Video & Audio Downloader

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-Latest-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://github.com/yt-dlp/yt-dlp)
[![HTML5/JS](https://img.shields.io/badge/Frontend-HTML5%20%2F%20JS-E34F26?style=for-the-badge&logo=html5&logoColor=white)](#-frontend)
[![License](https://img.shields.io/badge/License-MIT-blue.style=for-the-badge)](#)

O **dTube** é uma aplicação web completa, moderna e de alta performance para extração de metadados e download de vídeos e áudios do YouTube. O projeto consiste em um **Backend RESTful assíncrono** construído em **FastAPI** e **yt-dlp**, e um **Frontend responsivo com design clean** em **HTML5, CSS3 e Vanilla JavaScript**.

---

## 📌 Conteúdo

- [✨ Funcionalidades principais](#-funcionalidades-principais)
- [🏗️ Arquitetura do Projeto](#️-arquitetura-do-projeto)
- [🛠️ Tecnologias Utilizadas](#️-tecnologias-utilizadas)
- [📋 Pré-requisitos](#-pré-requisitos)
- [🚀 Instalação e Execução](#-instalação-e-execução)
  - [1. Clonar o Repositório](#1-clonar-o-repositório)
  - [2. Configurar e Executar o Backend](#2-configurar-e-executar-o-backend)
  - [3. Executar o Frontend](#3-executar-o-frontend)
- [🛡️ Solução para Bloqueio Anti-Bot do YouTube](#️-solução-para-bloqueio-anti-bot-do-youtube-cookies)
- [📡 Documentação da API REST (Backend)](#-documentação-da-api-rest-backend)
- [⚙️ Configuração do Frontend](#️-configuração-do-frontend)
- [🧪 Executando os Testes](#-executando-os-testes)
- [🧹 Política de Limpeza Automática](#-política-de-limpeza-automática)

---

## ✨ Funcionalidades principais

### 🎥 Backend (FastAPI API)
* **Obtenção de Metadados (`GET /api/info`)**: Retorna título, autor, duração (segundos e `HH:MM:SS`), thumbnail, descrição e resoluções disponíveis (1080p, 720p, 480p, etc.).
* **Download de Vídeo e Áudio (`POST /api/download`)**: Suporta exportação em formato **MP4** (vídeo com áudio) e **MP3** (áudio extraído com FFmpeg).
* **Processamento Assíncrono**: Execução de chamadas intensivas do `yt-dlp` em threads dedicadas (`asyncio.to_thread`) sem bloquear o event loop do FastAPI.
* **Limpeza Automática de Disco**: Remoção imediata de arquivos temporários do servidor após o envio ao cliente via `BackgroundTask`.
* **Suporte a Cookies Netscape**: Ignora restrições anti-bot ("*Sign in to confirm you're not a bot*") utilizando `cookies.txt`.

### 🎨 Frontend (Interface Web)
* **Design Minimalista ("Tela Clean")**: Interface moderna com foco na usabilidade e experiência do usuário.
* **Validação de Links e Utilitários**: Validação automática de URLs do YouTube, botão de colar da área de transferência e botão de limpar.
* **File System Access API (`window.showSaveFilePicker`)**: Permite escolher a pasta de destino e nome do arquivo diretamente na janela nativa do sistema operacional (Windows Explorer / Finder).
* **Visualização de Informações**: Exibe thumbnail em alta qualidade, detalhes do canal, duração e badges de resolução.
* **Acompanhamento de Progresso Dinâmico**: Progresso em tempo real (0-100%), bytes baixados, tamanho total e taxa de transferência em MB/s.
* **Endpoint da API Ajustável**: Permite alterar o endereço do servidor backend dinamicamente pelo arquivo `config.js` ou diretamente pela interface do navegador.

---

## 🏗️ Arquitetura do Projeto

```text
dTube/
├── backend/                  # API RESTful (FastAPI + yt-dlp)
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes.py     # Endpoints (/api/info e /api/download)
│   │   │   └── schemas.py    # Modelos Pydantic V2 de requisição e resposta
│   │   ├── services/
│   │   │   └── youtube_service.py # Lógica de extração e download com yt-dlp
│   │   ├── utils/
│   │   │   └── helpers.py    # Utilitários (validação de URL, formatação, limpeza)
│   │   ├── __init__.py
│   │   └── main.py           # Ponto de entrada FastAPI e configurações de CORS
│   ├── tests/
│   │   └── test_api.py       # Suíte de testes integrados com Pytest
│   ├── .gitignore            # Regras de ignorados do backend
│   ├── pytest.ini            # Configurações do ambiente de testes
│   ├── README.md             # Documentação específica do backend
│   └── requirements.txt      # Dependências Python
│
├── frontend/                 # Interface do Usuário (HTML5 / CSS3 / JS)
│   ├── app.js                # Lógica da UI, requisições Fetch, streaming e salva de arquivos
│   ├── config.js             # Configurações centrais do frontend (API Endpoint)
│   ├── index.html            # Estrutura da página web principal
│   ├── README.md             # Documentação específica do frontend
│   ├── server.py             # Servidor HTTP simples em Python para desenvolvimento
│   └── styles.css            # Estilização responsiva e tema clean
│
├── .gitignore                # Regras de ignorados do repositório raiz
└── README.md                 # Documentação principal do projeto
```

---

## 🛠️ Tecnologias Utilizadas

### Backend
* **[Python 3.10+](https://www.python.org/)**
* **[FastAPI](https://fastapi.tiangolo.com/)** — Framework web assíncrono de alto desempenho.
* **[Uvicorn](https://www.uvicorn.org/)** — Servidor ASGI ultrarrápido.
* **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** — Engine avançada para download de mídias do YouTube.
* **[Pydantic V2](https://docs.pydantic.dev/)** — Validação e serialização de dados com tipagem forte.
* **[Pytest](https://docs.pytest.org/)** — Framework para testes automatizados.

### Frontend
* **HTML5 / CSS3** — Estrutura semântica e estilização moderna.
* **Vanilla JavaScript (ES6+)** — Manipulação DOM e consumo da API via `fetch`.
* **Web File System Access API** — Salvar arquivos diretamente no sistema de arquivos local.
* **Python HTTP Server** — Servidor local leve para servir os estáticos do frontend.

---

## 📋 Pré-requisitos

Antes de iniciar, certifique-se de ter os seguintes componentes instalados no seu ambiente:

1. **Python 3.10 ou superior**: [Download Python](https://www.python.org/downloads/)
2. **FFmpeg**: Necessário para extração de áudio em MP3 e mesclagem de vídeo/áudio em altas resoluções (1080p+).

### Instalando o FFmpeg

- **Windows (via Winget)**:
  ```powershell
  winget install ffmpeg
  ```
- **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt update && sudo apt install -y ffmpeg
  ```
- **macOS (via Homebrew)**:
  ```bash
  brew install ffmpeg
  ```

---

## 🚀 Instalação e Execução

### 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/dTube.git
cd dTube
```

---

### 2. Configurar e Executar o Backend

1. **Acessar a pasta do backend**:
   ```bash
   cd backend
   ```

2. **Criar e ativar o ambiente virtual (venv)**:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Instalar as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Iniciar o servidor da API**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   > 🌐 O backend estará disponível em: `http://localhost:8000`  
   > 📄 Documentação interativa Swagger: `http://localhost:8000/docs`

---

### 3. Executar o Frontend

1. Abra um novo terminal na pasta raiz do projeto (`dTube`).
2. Acesse a pasta do frontend:
   ```bash
   cd frontend
   ```
3. Inicie o servidor HTTP local:
   ```bash
   python server.py
   ```
4. Acesse a aplicação no seu navegador:
   > 🌐 `http://localhost:3000`

*(Alternativamente, você também pode abrir o arquivo `frontend/index.html` diretamente em qualquer navegador moderno).*

---

## 🛡️ Solução para Bloqueio Anti-Bot do YouTube (Cookies)

Algumas conexões ou vídeos do YouTube exigem autenticação / cookies de sessão para evitar o bloqueio `Sign in to confirm you're not a bot`.

### Como configurar os cookies:

1. **Instalar uma extensão de exportação de cookies**:
   - Instale a extensão no seu navegador (Chrome/Edge/Firefox): **"Get cookies.txt LOCALLY"**.
2. **Exportar os cookies do YouTube**:
   - Acesse [YouTube.com](https://www.youtube.com) estando logado na sua conta.
   - Clique no ícone da extensão e escolha a opção **Export** para salvar o arquivo `cookies.txt`.
3. **Adicionar o arquivo ao Backend**:
   - Mova o arquivo gerado para a pasta `backend/` e renomeie-o para **`cookies.txt`** (caminho: `backend/cookies.txt`).
   - O `dTube` detectará o arquivo automaticamente e o utilizará nas requisições ao `yt-dlp`.

---

## 📡 Documentação da API REST (Backend)

### Endpoints Principais

#### 1. `GET /`
- **Descrição**: Health check da API.
- **Resposta**:
  ```json
  {
    "status": "online",
    "service": "YouTube Downloader API",
    "version": "1.0.0",
    "documentation": "/docs"
  }
  ```

#### 2. `GET /api/info`
- **Descrição**: Obtém metadados e formatos disponíveis de um vídeo.
- **Parâmetros Query**:
  - `url` (obrigatório): URL do vídeo do YouTube. Exemplo: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- **Exemplo de Resposta**:
  ```json
  {
    "id": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up",
    "uploader": "Rick Astley",
    "duration": 213,
    "duration_formatted": "03:33",
    "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
    "description": "The official video for...",
    "available_formats": ["1080p", "720p", "480p", "360p"]
  }
  ```

#### 3. `POST /api/download`
- **Descrição**: Faz o download do arquivo de vídeo ou extrai o áudio e o envia como stream (`FileResponse`).
- **Body (`application/json`)**:
  ```json
  {
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "format": "mp4",
    "quality": "1080p"
  }
  ```
  *(Formatos aceitos: `"mp4"` ou `"mp3"`. Qualidades aceitas: `"best"`, `"1080p"`, `"720p"`, etc.)*
- **Resposta**: Stream de download do arquivo (`application/octet-stream` ou `video/mp4` / `audio/mpeg`).

---

## ⚙️ Configuração do Frontend

A URL base da API consultada pelo frontend é definida no arquivo `frontend/config.js`:

```javascript
const CONFIG = {
  API_BASE_URL: "http://localhost:8000/api",
  TIMEOUT_MS: 300000
};
```

Você pode:
1. **Alterar no código**: Editar o arquivo `frontend/config.js`.
2. **Alterar pela UI**: Clicar no botão **"Alterar API"** localizado no rodapé do frontend para definir um novo endpoint via modal interativo.

---

## 🧪 Executando os Testes

Para executar os testes automatizados do backend:

1. Certifique-se de que o ambiente virtual está ativo na pasta `backend/`.
2. Execute o Pytest:
   ```bash
   pytest
   ```

---

## 🧹 Política de Limpeza Automática

Para garantir o bom uso do armazenamento no servidor:
- Durante o download, o backend cria um diretório temporário isolado em `temp_downloads/` ou no diretório temporário do SO.
- Após a transferência do arquivo ser finalizada pelo cliente, uma `BackgroundTask` do Starlette/FastAPI remove o diretório temporário imediatamente.

---

## 📄 Licença

Este projeto é desenvolvido para fins educacionais e de uso pessoal sob a licença MIT.
