(() => {
  const cfg = window.PANTRA_DEMO;
  const messagesEl = document.getElementById("messages");
  const inputEl = document.getElementById("text-input");
  const sendBtn = document.getElementById("send-btn");
  const recordBtn = document.getElementById("record-btn");
  const inputBar = document.querySelector(".chat-input");

  const WAVEFORM_BARS = 56;

  // ─── Recording state ────────────────────────────────────────────────
  let mediaRecorder = null;
  let recordedChunks = [];
  let recordStream = null;
  let recordMime = "audio/webm";
  let audioCtx = null;
  let analyser = null;
  let timeBuf = null;
  let history = new Float32Array(WAVEFORM_BARS);
  let recording = false;
  let paused = false;
  let cancelled = false;
  let rafId = null;
  let activeMs = 0;
  let lastFrameAt = 0;
  let toolbar = null;
  let canvasCtx = null;
  let canvasW = 0;
  let canvasH = 0;
  let canvasDpr = 1;

  // ─── Bubble helpers ─────────────────────────────────────────────────
  function appendTextBubble(side, text) {
    const bubble = document.createElement("div");
    bubble.className = `bubble bubble-${side}`;
    bubble.textContent = text;
    messagesEl.appendChild(bubble);
    scrollToBottom();
    return bubble;
  }

  function appendAudioBubble(side, url) {
    const bubble = document.createElement("div");
    bubble.className = `bubble bubble-${side} bubble-audio`;
    bubble.appendChild(buildAudioPlayer(url));
    messagesEl.appendChild(bubble);
    scrollToBottom();
    return bubble;
  }

  function appendSystem(text) {
    const b = document.createElement("div");
    b.className = "bubble bubble-system";
    b.textContent = text;
    messagesEl.appendChild(b);
    scrollToBottom();
  }

  function appendTyping() {
    const b = document.createElement("div");
    b.className = "bubble bubble-bot typing";
    messagesEl.appendChild(b);
    scrollToBottom();
    return b;
  }

  function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  // ─── Custom audio player ────────────────────────────────────────────
  function buildAudioPlayer(src) {
    const wrap = document.createElement("div");
    wrap.className = "audio-player";

    const audio = document.createElement("audio");
    audio.src = src;
    audio.preload = "metadata";

    const playBtn = document.createElement("button");
    playBtn.type = "button";
    playBtn.className = "audio-play";
    playBtn.setAttribute("aria-label", "Reproducir");
    playBtn.textContent = "▶";

    const track = document.createElement("div");
    track.className = "audio-track";
    const fill = document.createElement("div");
    fill.className = "audio-fill";
    track.appendChild(fill);

    const time = document.createElement("span");
    time.className = "audio-time";
    time.textContent = "0:00";

    wrap.append(audio, playBtn, track, time);

    let knownDuration = 0;

    audio.addEventListener("loadedmetadata", () => {
      knownDuration = isFinite(audio.duration) ? audio.duration : 0;
      time.textContent = fmt(knownDuration);
    });
    audio.addEventListener("timeupdate", () => {
      const d = isFinite(audio.duration) && audio.duration > 0 ? audio.duration : knownDuration;
      const ratio = d > 0 ? audio.currentTime / d : 0;
      fill.style.width = `${Math.min(100, ratio * 100)}%`;
      const remaining = Math.max(0, d - audio.currentTime);
      time.textContent = fmt(audio.paused ? d : remaining);
    });
    audio.addEventListener("ended", () => {
      playBtn.textContent = "▶";
      fill.style.width = "0%";
      time.textContent = fmt(knownDuration);
    });

    playBtn.addEventListener("click", () => {
      if (audio.paused) {
        audio.play();
        playBtn.textContent = "⏸";
      } else {
        audio.pause();
        playBtn.textContent = "▶";
      }
    });

    track.addEventListener("click", (e) => {
      const rect = track.getBoundingClientRect();
      const ratio = (e.clientX - rect.left) / rect.width;
      const d = isFinite(audio.duration) ? audio.duration : knownDuration;
      audio.currentTime = Math.max(0, Math.min(d, ratio * d));
    });

    return wrap;
  }

  function fmt(seconds) {
    if (!isFinite(seconds) || seconds < 0) seconds = 0;
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, "0")}`;
  }

  // ─── Send text ──────────────────────────────────────────────────────
  async function sendText() {
    const text = inputEl.value.trim();
    if (!text) return;
    inputEl.value = "";
    appendTextBubble("me", text);
    const typing = appendTyping();

    try {
      const r = await fetch(`/demo/${cfg.vertical}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, session_id: cfg.sessionId }),
      });
      const data = await r.json();
      typing.remove();
      renderReply(data);
    } catch (e) {
      typing.remove();
      appendSystem("Algo falló. Intentá de nuevo.");
    }
  }

  function renderReply(data) {
    if (data.handoff) {
      appendSystem("La conversación pasó a un humano.");
      return;
    }
    if (data.skipped) {
      appendSystem(`(${data.skipped})`);
      return;
    }
    if (data.text) appendTextBubble("bot", data.text);
    if (data.audio_url) appendAudioBubble("bot", data.audio_url);
  }

  // ─── Recording flow ─────────────────────────────────────────────────
  async function startRecording() {
    if (recording) return;
    if (!navigator.mediaDevices?.getUserMedia) {
      appendSystem("Tu navegador no soporta grabar audio.");
      return;
    }

    try {
      recordStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      appendSystem("No pude acceder al micrófono.");
      return;
    }

    recordMime = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
      ? "audio/webm;codecs=opus"
      : "audio/webm";
    mediaRecorder = new MediaRecorder(recordStream, { mimeType: recordMime });
    recordedChunks = [];
    cancelled = false;

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) recordedChunks.push(e.data);
    };
    mediaRecorder.onstop = onRecorderStop;

    // Spin up the analyser for real-time waveform.
    try {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const source = audioCtx.createMediaStreamSource(recordStream);
      analyser = audioCtx.createAnalyser();
      analyser.fftSize = 1024;
      analyser.smoothingTimeConstant = 0.6;
      timeBuf = new Uint8Array(analyser.fftSize);
      source.connect(analyser);
    } catch (e) {
      // No analyser — waveform won't animate but recording still works.
      console.warn("AudioContext unavailable", e);
    }

    history = new Float32Array(WAVEFORM_BARS);
    activeMs = 0;
    lastFrameAt = 0;
    paused = false;
    recording = true;

    showToolbar();
    mediaRecorder.start(100);
    rafId = requestAnimationFrame(tick);
  }

  function onRecorderStop() {
    const blob = recordedChunks.length
      ? new Blob(recordedChunks, { type: recordMime })
      : null;
    cleanupRecording();
    if (cancelled || !blob) return;
    uploadAudio(blob);
  }

  function cleanupRecording() {
    recording = false;
    paused = false;
    if (rafId) {
      cancelAnimationFrame(rafId);
      rafId = null;
    }
    recordStream?.getTracks().forEach((t) => t.stop());
    recordStream = null;
    if (audioCtx) {
      audioCtx.close().catch(() => {});
      audioCtx = null;
    }
    analyser = null;
    timeBuf = null;
    hideToolbar();
  }

  function pauseRecording() {
    if (!recording || mediaRecorder?.state !== "recording") return;
    mediaRecorder.pause();
    paused = true;
    updatePauseButton();
  }

  function resumeRecording() {
    if (!recording || mediaRecorder?.state !== "paused") return;
    mediaRecorder.resume();
    paused = false;
    lastFrameAt = 0; // restart frame delta after pause
    updatePauseButton();
  }

  function cancelRecording() {
    if (!recording) return;
    cancelled = true;
    if (mediaRecorder.state !== "inactive") mediaRecorder.stop();
  }

  function sendRecording() {
    if (!recording) return;
    cancelled = false;
    if (mediaRecorder.state !== "inactive") mediaRecorder.stop();
  }

  function updatePauseButton() {
    if (!toolbar) return;
    const btn = toolbar.querySelector(".rec-pause");
    btn.textContent = paused ? "▶" : "⏸";
    btn.setAttribute("aria-label", paused ? "Continuar" : "Pausar");
    toolbar.classList.toggle("is-paused", paused);
  }

  // ─── Toolbar UI ─────────────────────────────────────────────────────
  function showToolbar() {
    toolbar = document.createElement("div");
    toolbar.className = "recording-toolbar";
    toolbar.innerHTML = `
      <button type="button" class="rec-cancel" aria-label="Cancelar">🗑</button>
      <span class="rec-dot" aria-hidden="true"></span>
      <span class="rec-time">0:00</span>
      <canvas class="rec-waveform"></canvas>
      <button type="button" class="rec-pause" aria-label="Pausar">⏸</button>
      <button type="button" class="rec-send" aria-label="Enviar">➤</button>
    `;
    inputBar.appendChild(toolbar);

    toolbar.querySelector(".rec-cancel").addEventListener("click", cancelRecording);
    toolbar.querySelector(".rec-pause").addEventListener("click", () => {
      paused ? resumeRecording() : pauseRecording();
    });
    toolbar.querySelector(".rec-send").addEventListener("click", sendRecording);

    setupCanvas(toolbar.querySelector(".rec-waveform"));
  }

  function hideToolbar() {
    if (toolbar) {
      toolbar.remove();
      toolbar = null;
    }
    canvasCtx = null;
  }

  function setupCanvas(canvas) {
    canvasDpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvasW = rect.width || 200;
    canvasH = rect.height || 32;
    canvas.width = canvasW * canvasDpr;
    canvas.height = canvasH * canvasDpr;
    canvasCtx = canvas.getContext("2d");
    canvasCtx.scale(canvasDpr, canvasDpr);
  }

  // ─── Render loop ────────────────────────────────────────────────────
  function tick(now) {
    if (!recording) return;

    if (lastFrameAt && !paused) {
      activeMs += now - lastFrameAt;
    }
    lastFrameAt = now;

    if (analyser && !paused) {
      analyser.getByteTimeDomainData(timeBuf);
      let sum = 0;
      for (let i = 0; i < timeBuf.length; i++) {
        const v = (timeBuf[i] - 128) / 128;
        sum += v * v;
      }
      const rms = Math.sqrt(sum / timeBuf.length);
      // Shift left, push newest at the end (most recent on the right).
      for (let i = 0; i < WAVEFORM_BARS - 1; i++) history[i] = history[i + 1];
      history[WAVEFORM_BARS - 1] = rms;
    }

    drawWaveform();

    if (toolbar) {
      const t = toolbar.querySelector(".rec-time");
      if (t) t.textContent = fmt(activeMs / 1000);
    }

    rafId = requestAnimationFrame(tick);
  }

  function drawWaveform() {
    if (!canvasCtx) return;
    const ctx = canvasCtx;
    ctx.clearRect(0, 0, canvasW, canvasH);

    const slot = canvasW / WAVEFORM_BARS;
    const barW = Math.max(1.5, slot * 0.55);
    const minBarH = 2;
    const amplification = 2.2;
    ctx.fillStyle = paused ? "#9aa6ad" : "#128C7E";

    for (let i = 0; i < WAVEFORM_BARS; i++) {
      // Slight curve so quiet noise stays visible without blowing up loud.
      const amp = Math.sqrt(history[i]);
      const barH = Math.max(minBarH, Math.min(canvasH, amp * canvasH * amplification));
      const x = i * slot + (slot - barW) / 2;
      const y = (canvasH - barH) / 2;
      ctx.fillRect(x, y, barW, barH);
    }
  }

  // ─── Upload ─────────────────────────────────────────────────────────
  async function uploadAudio(blob) {
    const localUrl = URL.createObjectURL(blob);
    appendAudioBubble("me", localUrl);
    const typing = appendTyping();

    const fd = new FormData();
    fd.append("audio", blob, "voice.webm");
    fd.append("session_id", cfg.sessionId);
    try {
      const r = await fetch(`/demo/${cfg.vertical}/audio`, {
        method: "POST",
        body: fd,
      });
      const data = await r.json();
      typing.remove();
      renderReply(data);
    } catch (e) {
      typing.remove();
      appendSystem("Algo falló al procesar el audio.");
    }
  }

  // ─── Reset (new conversation) ───────────────────────────────────────
  async function resetConversation() {
    if (!confirm("¿Empezar una nueva conversación? Se borra el contexto actual.")) return;
    try {
      await fetch(`/demo/${cfg.vertical}/reset`, { method: "POST" });
    } catch (e) {
      // even if it fails server-side, reload — cookie is gone client-side too
    }
    window.location.reload();
  }

  // ─── Events ─────────────────────────────────────────────────────────
  sendBtn.addEventListener("click", sendText);
  inputEl.addEventListener("keydown", (e) => { if (e.key === "Enter") sendText(); });
  recordBtn.addEventListener("click", startRecording);

  document.getElementById("reset-btn")?.addEventListener("click", resetConversation);
})();
