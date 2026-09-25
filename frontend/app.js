/**
 * YouTube Downloader - Lógica Principal do Frontend
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elementos da Interface
  const urlInput = document.getElementById("url-input");
  const btnPaste = document.getElementById("btn-paste");
  const btnClear = document.getElementById("btn-clear");
  const formatSelect = document.getElementById("format-select");
  const qualitySelect = document.getElementById("quality-select");
  const btnInfo = document.getElementById("btn-info");
  const btnInfoText = document.getElementById("btn-info-text");
  const btnDownload = document.getElementById("btn-download");
  const btnDownloadText = document.getElementById("btn-download-text");
  
  // Elementos do Card de Vídeo
  const videoCard = document.getElementById("video-card");
  const videoThumbnail = document.getElementById("video-thumbnail");
  const videoDuration = document.getElementById("video-duration");
  const videoTitle = document.getElementById("video-title");
  const videoAuthor = document.getElementById("video-author");
  const formatsTags = document.getElementById("formats-tags");

  // Elementos da Barra de Progresso
  const progressCard = document.getElementById("progress-card");
  const progressStatus = document.getElementById("progress-status");
  const statusSpinner = document.getElementById("status-spinner");
  const progressPercent = document.getElementById("progress-percent");
  const progressBarFill = document.getElementById("progress-bar-fill");
  const progressBytes = document.getElementById("progress-bytes");
  const progressSpeed = document.getElementById("progress-speed");

  // Alertas e Rodapé
  const alertBox = document.getElementById("alert-box");
  const alertMessage = document.getElementById("alert-message");
  const apiEndpointLabel = document.getElementById("api-endpoint-label");
  const btnChangeApi = document.getElementById("btn-change-api");

  // Estado da Aplicação
  let currentVideoInfo = null;
  let isProcessing = false;

  // Carregar API configurada do localStorage, se houver
  const savedApiUrl = localStorage.getItem("YOUTUBE_DOWNLOADER_API");
  if (savedApiUrl) {
    CONFIG.API_BASE_URL = savedApiUrl;
  }
  apiEndpointLabel.textContent = CONFIG.API_BASE_URL;

  // =========================================================================
  // Utilitários
  // =========================================================================

  function cleanErrorMessage(msg) {
    if (!msg) return "";
    return msg
      .replace(/\x1B\[[0-9;]*[mK]/g, "")
      .replace(/\[\d+;\d+m/g, "")
      .replace(/\[0m/g, "")
      .trim();
  }

  function showAlert(message, type = "error") {
    alertBox.className = `alert alert-${type}`;
    alertMessage.textContent = message;
    alertBox.classList.remove("hidden");
  }

  function hideAlert() {
    alertBox.classList.add("hidden");
  }

  function formatBytes(bytes) {
    if (!bytes || bytes === 0) return "0 MB";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
  }

  function sanitizeFilename(name) {
    if (!name) return "youtube_video";
    // Remove caracteres inválidos no Windows: \ / : * ? " < > |
    return name
      .replace(/[\\/:*?"<>|]/g, "_")
      .replace(/\s+/g, " ")
      .trim();
  }

  function isValidYouTubeUrl(url) {
    if (!url) return false;
    const pattern = /^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?.*v=|shorts\/)|youtu\.be\/)[a-zA-Z0-9_-]+/;
    return pattern.test(url.trim());
  }

  // =========================================================================
  // Gerenciamento de Opções de Formato e Qualidade
  // =========================================================================

  formatSelect.addEventListener("change", () => {
    const isMp3 = formatSelect.value === "mp3";
    qualitySelect.innerHTML = "";

    if (isMp3) {
      qualitySelect.innerHTML = `
        <option value="bestaudio" selected>Melhor Áudio Disponível (bestaudio)</option>
        <option value="320k">Alta Qualidade (320 kbps)</option>
        <option value="192k">Média Qualidade (192 kbps)</option>
        <option value="128k">Padrão (128 kbps)</option>
      `;
    } else {
      // Se tivermos as resoluções do vídeo atual, usa elas
      if (currentVideoInfo && currentVideoInfo.formats) {
        populateVideoQualities(currentVideoInfo.formats);
      } else {
        qualitySelect.innerHTML = `
          <option value="best" selected>Melhor Qualidade (Padrão)</option>
          <option value="1080p">1080p Full HD</option>
          <option value="720p">720p HD</option>
          <option value="480p">480p</option>
          <option value="360p">360p</option>
        `;
      }
    }
  });

  function populateVideoQualities(formats) {
    const isMp3 = formatSelect.value === "mp3";
    if (isMp3) return;

    qualitySelect.innerHTML = `<option value="best" selected>Melhor Qualidade (Padrão)</option>`;

    // Extrair resoluções únicas disponíveis com vídeo
    const resolutions = new Set();
    formats.forEach(f => {
      if (f.resolution && f.has_video) {
        const match = f.resolution.match(/(\d{3,4}p)/);
        if (match) {
          resolutions.add(match[1]);
        }
      }
    });

    // Ordenar de forma decrescente (ex: 1080p, 720p, 480p)
    const sorted = Array.from(resolutions).sort((a, b) => {
      return parseInt(b) - parseInt(a);
    });

    sorted.forEach(res => {
      const opt = document.createElement("option");
      opt.value = res;
      opt.textContent = `${res} ${res === "1080p" ? "Full HD" : res === "720p" ? "HD" : ""}`;
      qualitySelect.appendChild(opt);
    });
  }

  // =========================================================================
  // Interações de Entrada (Colar / Limpar / Auto-Detect)
  // =========================================================================

  btnPaste.addEventListener("click", async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        urlInput.value = text.trim();
        hideAlert();
        if (isValidYouTubeUrl(text)) {
          fetchVideoInfo(text.trim());
        }
      }
    } catch (err) {
      showAlert("Não foi possível acessar a área de transferência. Cole manualmente.", "warning");
    }
  });

  btnClear.addEventListener("click", () => {
    urlInput.value = "";
    videoCard.classList.add("hidden");
    progressCard.classList.add("hidden");
    currentVideoInfo = null;
    hideAlert();
    urlInput.focus();
  });

  urlInput.addEventListener("input", () => {
    hideAlert();
  });

  urlInput.addEventListener("paste", (e) => {
    setTimeout(() => {
      const val = urlInput.value.trim();
      if (isValidYouTubeUrl(val)) {
        fetchVideoInfo(val);
      }
    }, 100);
  });

  // =========================================================================
  // Buscar Metadados do Vídeo
  // =========================================================================

  async function fetchVideoInfo(urlToFetch) {
    const url = urlToFetch || urlInput.value.trim();
    if (!url) {
      showAlert("Por favor, cole um link do YouTube primeiro.");
      urlInput.focus();
      return null;
    }

    if (!isValidYouTubeUrl(url)) {
      showAlert("O link inserido não parece ser um link válido do YouTube.");
      return null;
    }

    hideAlert();
    btnInfo.disabled = true;
    btnInfoText.textContent = "Buscando...";

    try {
      const response = await fetch(`${CONFIG.API_BASE_URL}/info?url=${encodeURIComponent(url)}`, {
        method: "GET",
        headers: { "Accept": "application/json" }
      });

      if (!response.ok) {
        let errorMsg = "Erro ao buscar informações do vídeo.";
        try {
          const errData = await response.json();
          if (errData.detail) errorMsg = errData.detail;
        } catch (_) {}
        throw new Error(errorMsg);
      }

      const data = await response.json();
      currentVideoInfo = data;

      // Atualizar Card de Informações
      videoThumbnail.src = data.thumbnail || "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=600&q=80";
      videoDuration.textContent = data.duration_formatted || "00:00";
      videoTitle.textContent = data.title;
      videoAuthor.textContent = data.channel;

      // Listar badges de formatos
      formatsTags.innerHTML = "";
      if (data.formats && data.formats.length > 0) {
        populateVideoQualities(data.formats);

        // Tags resumidas
        const badges = new Set();
        data.formats.forEach(f => {
          if (f.resolution && f.has_video) {
            const m = f.resolution.match(/(\d{3,4}p)/);
            if (m) badges.add(m[1]);
          }
        });
        badges.forEach(b => {
          const tag = document.createElement("span");
          tag.className = "format-tag";
          tag.textContent = b;
          formatsTags.appendChild(tag);
        });

        // Adicionar badge de MP3
        const mp3Tag = document.createElement("span");
        mp3Tag.className = "format-tag";
        mp3Tag.textContent = "Áudio MP3";
        formatsTags.appendChild(mp3Tag);
      }

      videoCard.classList.remove("hidden");
      return data;
    } catch (err) {
      console.error(err);
      const clean = cleanErrorMessage(err.message);
      if (clean.includes("confirm you") || clean.includes("not a bot")) {
        showAlert("O YouTube bloqueou este vídeo exigindo verificação anti-bot. Tente outro vídeo ou configure cookies no backend.");
      } else if (err.name === "TypeError" && (clean.includes("fetch") || clean.includes("NetworkError") || clean.includes("Failed"))) {
        showAlert(`Não foi possível conectar ao backend. Verifique se a API está online em ${CONFIG.API_BASE_URL}.`);
      } else {
        showAlert(`Erro: ${clean}`);
      }
      return null;
    } finally {
      btnInfo.disabled = false;
      btnInfoText.textContent = "Buscar Informações";
    }
  }

  btnInfo.addEventListener("click", () => fetchVideoInfo());

  // =========================================================================
  // Download do Vídeo com Explorador de Arquivos e Barra de Progresso
  // =========================================================================

  btnDownload.addEventListener("click", async () => {
    if (isProcessing) return;

    const url = urlInput.value.trim();
    if (!url) {
      showAlert("Por favor, informe o link do YouTube para baixar.");
      urlInput.focus();
      return;
    }

    if (!isValidYouTubeUrl(url)) {
      showAlert("Link do YouTube inválido.");
      return;
    }

    hideAlert();

    // 1. Garantir que temos metadados para sugerir o nome do arquivo correto
    let videoInfo = currentVideoInfo;
    if (!videoInfo || videoInfo.url !== url) {
      videoInfo = await fetchVideoInfo(url);
      if (!videoInfo) return; // Erro já mostrado no fetchVideoInfo
    }

    const format = formatSelect.value; // 'mp4' ou 'mp3'
    const quality = qualitySelect.value; // 'best', '1080p', etc.
    const isMp3 = format === "mp3";
    const extension = isMp3 ? "mp3" : "mp4";
    const suggestedFilename = `${sanitizeFilename(videoInfo.title)}.${extension}`;

    // 2. Abrir o Explorador de Arquivos do Sistema (showSaveFilePicker)
    let fileHandle = null;
    let writableStream = null;

    if ("showSaveFilePicker" in window) {
      try {
        const pickerOptions = {
          suggestedName: suggestedFilename,
          types: [{
            description: isMp3 ? "Arquivo de Áudio MP3 (*.mp3)" : "Arquivo de Vídeo MP4 (*.mp4)",
            accept: {
              [isMp3 ? "audio/mpeg" : "video/mp4"]: [`.${extension}`]
            }
          }]
        };

        fileHandle = await window.showSaveFilePicker(pickerOptions);
        writableStream = await fileHandle.createWritable();
      } catch (err) {
        if (err.name === "AbortError") {
          showAlert("Download cancelado: nenhuma pasta de destino foi selecionada.", "info");
          return;
        }
        console.warn("Acesso direto ao sistema de arquivos não permitido, usando download tradicional.", err);
      }
    }

    // 3. Iniciar o Download e Exibir a Barra de Progresso
    setProcessingState(true);
    progressCard.classList.remove("hidden");
    progressBarFill.style.width = "0%";
    progressBarFill.classList.add("indeterminate");
    progressPercent.textContent = "0%";
    progressBytes.textContent = "Iniciando...";
    progressSpeed.textContent = "-- MB/s";
    progressStatus.textContent = "Conectando ao servidor e processando mídia...";
    statusSpinner.style.display = "inline-block";

    try {
      const response = await fetch(`${CONFIG.API_BASE_URL}/download`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          url: url,
          format: format,
          quality: quality
        })
      });

      if (!response.ok) {
        let errorMsg = "Falha no download da mídia.";
        try {
          const errJson = await response.json();
          if (errJson.detail) errorMsg = errJson.detail;
        } catch (_) {}
        throw new Error(errorMsg);
      }

      // Identificar o tamanho total
      const contentLengthHeader = response.headers.get("content-length");
      const totalBytes = contentLengthHeader ? parseInt(contentLengthHeader, 10) : 0;

      progressBarFill.classList.remove("indeterminate");
      progressStatus.textContent = "Gravando arquivo no computador...";

      const reader = response.body.getReader();
      let receivedBytes = 0;
      const startTime = performance.now();
      const chunks = []; // Para fallback caso não tenha showSaveFilePicker

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        receivedBytes += value.length;

        // Se tiver stream gravável do FilePicker, grava o chunk diretamente no disco
        if (writableStream) {
          await writableStream.write(value);
        } else {
          chunks.push(value);
        }

        // Atualizar barra de progresso
        if (totalBytes > 0) {
          const percent = Math.min(100, Math.round((receivedBytes / totalBytes) * 100));
          progressBarFill.style.width = `${percent}%`;
          progressPercent.textContent = `${percent}%`;
          progressBytes.textContent = `${formatBytes(receivedBytes)} de ${formatBytes(totalBytes)}`;
        } else {
          progressBytes.textContent = `${formatBytes(receivedBytes)} baixados`;
          progressPercent.textContent = "";
        }

        // Calcular velocidade
        const elapsedSec = (performance.now() - startTime) / 1000;
        if (elapsedSec > 0.5) {
          const speedBytesPerSec = receivedBytes / elapsedSec;
          progressSpeed.textContent = `${formatBytes(speedBytesPerSec)}/s`;
        }
      }

      // Concluir gravação no disco
      if (writableStream) {
        await writableStream.close();
      } else {
        // Fallback: Disparar download pelo navegador via Blob
        const blob = new Blob(chunks, { type: isMp3 ? "audio/mpeg" : "video/mp4" });
        const downloadUrl = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = suggestedFilename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(downloadUrl);
      }

      // Sucesso Total
      progressBarFill.style.width = "100%";
      progressPercent.textContent = "100%";
      progressStatus.textContent = "Download concluído com sucesso!";
      statusSpinner.style.display = "none";
      showAlert(`Arquivo "${suggestedFilename}" salvo com sucesso!`, "success");

    } catch (err) {
      console.error("Erro no download:", err);
      // Se o writableStream falhou, fechar
      if (writableStream) {
        try { await writableStream.abort(); } catch (_) {}
      }
      progressStatus.textContent = "Erro no download";
      statusSpinner.style.display = "none";
      const clean = cleanErrorMessage(err.message);
      if (clean.includes("confirm you") || clean.includes("not a bot")) {
        showAlert("O YouTube bloqueou o download deste vídeo exigindo verificação anti-bot. Tente outro vídeo ou configure cookies no backend.");
      } else {
        showAlert(`Falha: ${clean}`);
      }
    } finally {
      setProcessingState(false);
    }
  });

  function setProcessingState(processing) {
    isProcessing = processing;
    btnDownload.disabled = processing;
    btnInfo.disabled = processing;
    formatSelect.disabled = processing;
    qualitySelect.disabled = processing;
    btnDownloadText.textContent = processing ? "Processando..." : "Iniciar Download";
  }

  // =========================================================================
  // Configuração da URL da API (Modal/Prompt)
  // =========================================================================

  btnChangeApi.addEventListener("click", (e) => {
    e.preventDefault();
    const current = CONFIG.API_BASE_URL;
    const newUrl = prompt("Informe a URL base da API do YouTube Downloader:", current);
    if (newUrl && newUrl.trim() !== "") {
      const sanitizedUrl = newUrl.trim().replace(/\/$/, "");
      CONFIG.API_BASE_URL = sanitizedUrl;
      localStorage.setItem("YOUTUBE_DOWNLOADER_API", sanitizedUrl);
      apiEndpointLabel.textContent = sanitizedUrl;
      showAlert(`URL da API alterada para: ${sanitizedUrl}`, "info");
    }
  });

});
