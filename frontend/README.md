# Frontend - YouTube Video Downloader

Frontend moderno, limpo ("tela em branco") e responsivo desenvolvido com **HTML5 puro, CSS3 e Vanilla JavaScript** para integração com a API de download do YouTube em FastAPI.

---

## 🚀 Funcionalidades

- **Tela Clean ("Tela em branco")**: Interface moderna e minimalista com foco total na usabilidade.
- **Entrada de Link Inteligente**: Campo com validação automática de links do YouTube, botão de colar da área de transferência e botão de limpar.
- **Explorador de Arquivos do Sistema Operacional**: Utiliza a moderna *Web File System Access API* (`window.showSaveFilePicker`), permitindo escolher onde salvar o arquivo e com qual nome diretamente pelo Windows Explorer.
- **Espaço de Informações do Vídeo**: Exibe thumbnail, duração formatada, título, canal e badges de resoluções disponíveis (1080p, 720p, etc.).
- **Barra de Progresso Dinâmica**: Acompanhamento em tempo real com porcentagem (0-100%), bytes baixados, tamanho total e taxa de transferência (MB/s).
- **Opções de Download**: Suporte para download em formato **Vídeo (MP4)** em várias qualidades ou extração apenas de **Áudio (MP3)**.
- **API Configurável**: Configuração central no `config.js` e botão interativo no rodapé para alterar o endpoint da API dinamicamente via navegador.

---

## 📁 Estrutura de Arquivos

```text
front_down_youtube/
│
├── index.html       # Estrutura HTML da tela principal
├── styles.css       # Estilos visuais e responsividade (tema minimalista)
├── app.js           # Lógica de download, showSaveFilePicker e barra de progresso
├── config.js        # Configuração da URL da API
├── server.py        # Servidor web local simples em Python
└── README.md        # Documentação do projeto
```

---

## 🛠️ Como Executar

### 1. Iniciar a API Backend (Pasta `down_youtube`)
No terminal ou PowerShell, vá até a pasta do backend e inicie o servidor:
```bash
cd ..\down_youtube
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
A API estará rodando em `http://localhost:8000`.

### 2. Iniciar o Frontend (Pasta `front_down_youtube`)
Em outro terminal, execute o servidor local:
```bash
python server.py
```
Acesse a aplicação no navegador em: **`http://localhost:3000`**

*(Alternativamente, você também pode abrir o arquivo `index.html` diretamente no seu navegador).*

---

## ⚙️ Configuração da API

A URL padrão da API é configurada como:
`http://localhost:8000/api`

Para alterar:
1. Pelo arquivo: Edite `config.js` e altere a propriedade `API_BASE_URL`.
2. Pelo navegador: Clique em **"Alterar API"** no rodapé da página para definir uma nova URL.
