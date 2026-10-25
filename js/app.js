/**
 * MiniAgentLite - Interactive Client Application Logic
 * Menangani Simulator Tool Calling, Generator Konfigurasi, dan Navigasi Interaktif
 */

document.addEventListener("DOMContentLoaded", () => {
  initArchitectureInteractive();
  initSimulator();
  initConfigGenerator();
});

// =====================================================================
// 1. Interaktivitas Diagram Arsitektur
// =====================================================================
const archDetails = {
  user: {
    title: "1. Pengguna (Smartphone / Telegram)",
    desc: "Anda mengirimkan pesan bahasa alami santai dari aplikasi Telegram di smartphone, misalnya: 'Cek RAM PC saya' atau 'Screenshot layar'. Anda tidak perlu membuka terminal atau berada di depan komputer.",
    code: `# Pesan dikirim secara instan via enkripsi Telegram:
"Tolong screenshot layar monitor PC dong"`
  },
  telegram: {
    title: "2. Telegram Bot API",
    desc: "Telegram Bot API meneruskan pesan masuk ke script Python lokal di PC melalui metode Long Polling getUpdates tanpa membutuhkan IP publik, port forwarding, ataupun setup ngrok.",
    code: `# Endpoint Telegram Bot:
POST https://api.telegram.org/bot<TOKEN>/getUpdates`
  },
  agent: {
    title: "3. MiniAgentLite Runner (agent.py)",
    desc: "Jantung dari agen. Memeriksa whitelist ALLOWED_USER_IDS untuk memastikan orang asing tidak bisa membajak PC Anda. Mengirimkan percakapan beserta skema tools ke LLM dan mengeksekusi fungsi lokal.",
    code: `if user_id not in ALLOWED_USER_IDS:
    telegram.send_message(chat_id, "⛔ Akses Ditolak!")`
  },
  llm: {
    title: "4. LLM Engine (Gemini Flash Lite / Groq API)",
    desc: "Otak inferensi. Membaca pesan pengguna dan secara otomatis memilih apakah perlu memanggil tool hardware (Function Calling) atau cukup menjawab dengan teks biasa dalam hitungan milidetik (~300ms).",
    code: `// Respon LLM memicu Tool Calling:
"tool_calls": [{
  "name": "take_screenshot",
  "arguments": {}
}]`
  },
  tools: {
    title: "5. Tangan & Kaki PC (tools.py)",
    desc: "Eksekutor lokal di PC Anda. Mengakses API sistem operasi (Windows, Linux, macOS) untuk mengambil data hardware via psutil, screenshot via Pillow, buka browser via xdg-open/start, dan kontrol volume.",
    code: `def take_screenshot():
    img = ImageGrab.grab()
    img.save("pc_screenshot.png")
    return {"status": "success", "file": "pc_screenshot.png"}`
  }
};

function initArchitectureInteractive() {
  const nodes = document.querySelectorAll(".arch-node");
  const titleEl = document.getElementById("arch-detail-title");
  const descEl = document.getElementById("arch-detail-desc");
  const codeEl = document.getElementById("arch-detail-code");

  nodes.forEach(node => {
    node.addEventListener("click", () => {
      nodes.forEach(n => n.classList.remove("active"));
      node.classList.add("active");

      const nodeKey = node.getAttribute("data-node");
      const data = archDetails[nodeKey];
      if (data) {
        titleEl.textContent = data.title;
        descEl.textContent = data.desc;
        codeEl.innerHTML = `<code>${escapeHtml(data.code)}</code>`;
      }
    });
  });
}


// =====================================================================
// 2. Simulator Tool Calling Interaktif
// =====================================================================
function initSimulator() {
  const chatBody = document.getElementById("simChatBody");
  const simForm = document.getElementById("simForm");
  const simInput = document.getElementById("simInput");
  const presetChips = document.querySelectorAll(".preset-chip");
  const latencyBadge = document.getElementById("simLatencyBadge");
  const jsonPayloadEl = document.getElementById("simJsonPayload");
  const hwBoxEl = document.getElementById("simHwBox");
  const responsePreviewEl = document.getElementById("simResponsePreview");

  // Handle Preset Chips Click
  presetChips.forEach(chip => {
    chip.addEventListener("click", () => {
      const prompt = chip.getAttribute("data-prompt");
      simInput.value = prompt;
      runSimulation(prompt);
    });
  });

  // Handle Form Submit
  simForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = simInput.value.trim();
    if (!text) return;
    runSimulation(text);
    simInput.value = "";
  });

  function appendChatBubble(text, sender = "user") {
    const bubble = document.createElement("div");
    bubble.className = `chat-bubble ${sender}-bubble`;
    bubble.innerHTML = text;
    chatBody.appendChild(bubble);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  function runSimulation(promptText) {
    // 1. Tampilkan pesan user di chat bubble
    appendChatBubble(escapeHtml(promptText), "user");

    // 2. Set status loading pada inspector
    latencyBadge.textContent = "⚡ Memproses LLM...";
    latencyBadge.style.background = "rgba(56, 189, 248, 0.2)";
    latencyBadge.style.color = "#38bdf8";

    jsonPayloadEl.innerHTML = `<pre><code>// Mengirim prompt ke Gemini / Groq...</code></pre>`;
    hwBoxEl.innerHTML = `<div class="hw-idle">Menunggu keputusan function call dari LLM...</div>`;
    responsePreviewEl.textContent = "Sedang menunggu respon...";

    // Simulasi latensi ultra cepat (250ms - 450ms layaknya Flash Lite / Groq)
    const simulatedLatency = Math.floor(Math.random() * 150) + 260;

    setTimeout(() => {
      // 3. Tentukan tool mana yang dipicu berdasarkan kata kunci
      const toolMatch = analyzeToolFromPrompt(promptText);

      latencyBadge.textContent = `⚡ Latensi: ${simulatedLatency}ms`;
      latencyBadge.style.background = "rgba(16, 185, 129, 0.15)";
      latencyBadge.style.color = "#10b981";

      // 4. Update JSON Payload Box
      jsonPayloadEl.innerHTML = `<pre><code class="language-json">${escapeHtml(JSON.stringify(toolMatch.toolCall, null, 2))}</code></pre>`;

      // 5. Update Hardware Execution Visual
      hwBoxEl.innerHTML = toolMatch.hwHtml;

      // 6. Update Respon Balik ke Chat
      responsePreviewEl.textContent = toolMatch.replyText;
      appendChatBubble(toolMatch.replyHtml, "bot");

    }, simulatedLatency);
  }
}

function analyzeToolFromPrompt(prompt) {
  const p = prompt.toLowerCase();

  // 1. Status Hardware
  if (p.includes("ram") || p.includes("cpu") || p.includes("baterai") || p.includes("status") || p.includes("hardware")) {
    const cpu = Math.floor(Math.random() * 25) + 12;
    const ram = (Math.random() * 2 + 5.2).toFixed(1);
    return {
      toolCall: {
        function_call: {
          name: "get_system_status",
          arguments: {}
        }
      },
      hwHtml: `
        <div class="hw-active-card">
          <div style="font-size: 1.5rem;">📊</div>
          <div>
            <strong>tools.get_system_status() dieksekusi:</strong><br>
            <span style="color: #38bdf8;">CPU:</span> ${cpu}% &bull; 
            <span style="color: #10b981;">RAM Terpakai:</span> ${ram} GB / 16.0 GB &bull; 
            <span style="color: #f59e0b;">Baterai:</span> 88% (Tersambung Listrik)
          </div>
        </div>
      `,
      replyText: `Status PC: CPU ${cpu}%, RAM ${ram}/16GB, Baterai 88%`,
      replyHtml: `
        📊 <strong>Laporan Kondisi PC:</strong><br>
        • <strong>CPU:</strong> ${cpu}% (Sangat aman)<br>
        • <strong>RAM:</strong> ${ram} GB / 16.00 GB terpakai<br>
        • <strong>Disk:</strong> 245 GB sisa bebas (SSD)<br>
        • <strong>Baterai:</strong> 88% (Sedang Mengisi Daya)<br>
        • <strong>Uptime:</strong> 4 jam 12 menit
      `
    };
  }

  // 2. Screenshot
  if (p.includes("screenshot") || p.includes("tangkapan layar") || p.includes("foto")) {
    return {
      toolCall: {
        function_call: {
          name: "take_screenshot",
          arguments: { "output_path": "pc_screenshot.png" }
        }
      },
      hwHtml: `
        <div class="hw-active-card">
          <div style="font-size: 1.5rem;">📸</div>
          <div>
            <strong>tools.take_screenshot() dieksekusi:</strong><br>
            Resolusi: 1920x1080px &bull; File: <code>pc_screenshot.png</code> (342 KB)
          </div>
        </div>
      `,
      replyText: `Screenshot layar berhasil diambil dan dikirimkan ke Telegram.`,
      replyHtml: `
        📸 <strong>Screenshot Layar Monitor Berhasil Diambil!</strong><br>
        <div style="margin: 8px 0; background: #0f172a; padding: 12px; border-radius: 8px; border: 1px dashed #38bdf8; text-align: center;">
          <span style="color: #38bdf8; font-size: 0.85rem;">[ 🖼️ Gambar Screenshot Layar PC Terlampir (1920x1080) ]</span>
        </div>
        Layar utama sedang menampilkan browser dan desktop Anda.
      `
    };
  }

  // 3. Buka URL / Aplikasi
  if (p.includes("buka") || p.includes("open") || p.includes("browser") || p.includes("youtube") || p.includes("github")) {
    const target = p.includes("github") ? "https://github.com" : (p.includes("youtube") ? "https://youtube.com" : "Browser Default");
    return {
      toolCall: {
        function_call: {
          name: "open_application_or_url",
          arguments: { "target": target }
        }
      },
      hwHtml: `
        <div class="hw-active-card">
          <div style="font-size: 1.5rem;">🌐</div>
          <div>
            <strong>tools.open_application_or_url("${target}") dieksekusi:</strong><br>
            Browser default di PC Anda berhasil meluncurkan URL tersebut.
          </div>
        </div>
      `,
      replyText: `Berhasil membuka ${target} di browser PC Anda.`,
      replyHtml: `🌐 Siap bos! Halaman <strong>${target}</strong> sudah saya bukakan di layar monitor PC Anda.`
    };
  }

  // 4. Volume
  if (p.includes("volume") || p.includes("suara") || p.includes("speaker") || p.includes("kecilkan") || p.includes("besarkan")) {
    const levelMatch = prompt.match(/\d+/);
    const lvl = levelMatch ? parseInt(levelMatch[0]) : 25;
    return {
      toolCall: {
        function_call: {
          name: "set_volume",
          arguments: { "level": lvl }
        }
      },
      hwHtml: `
        <div class="hw-active-card">
          <div style="font-size: 1.5rem;">🔊</div>
          <div>
            <strong>tools.set_volume(${lvl}) dieksekusi:</strong><br>
            Audio driver sink master diset ke level ${lvl}%.
          </div>
        </div>
      `,
      replyText: `Volume PC diset ke ${lvl}%`,
      replyHtml: `🔊 Volume speaker PC Anda sudah berhasil diubah ke <strong>${lvl}%</strong>.`
    };
  }

  // 5. Notifikasi Desktop
  if (p.includes("notif") || p.includes("pesan") || p.includes("layar")) {
    return {
      toolCall: {
        function_call: {
          name: "send_desktop_notification",
          arguments: {
            "title": "MiniAgentLite",
            "message": "Pesan dari Telegram telah tiba!"
          }
        }
      },
      hwHtml: `
        <div class="hw-active-card">
          <div style="font-size: 1.5rem;">🔔</div>
          <div>
            <strong>tools.send_desktop_notification() dieksekusi:</strong><br>
            Toast pop-up muncul di pojok kanan bawah layar monitor PC.
          </div>
        </div>
      `,
      replyText: `Notifikasi terkirim ke monitor PC.`,
      replyHtml: `🔔 Banner notifikasi sudah dimunculkan di layar monitor PC Anda!`
    };
  }

  // Default / Execute Command
  return {
    toolCall: {
      function_call: {
        name: "execute_command",
        arguments: { "command": "uptime" }
      }
    },
    hwHtml: `
      <div class="hw-active-card">
        <div style="font-size: 1.5rem;">💻</div>
        <div>
          <strong>tools.execute_command("uptime") dieksekusi:</strong><br>
          Return Code: 0 (Success) &bull; Execution time: 14ms
        </div>
      </div>
    `,
    replyText: `Perintah berhasil dijalankan di PC.`,
    replyHtml: `💻 Perintah telah berhasil dieksekusi di PC Anda!<br><code>18:30:15 up 4:12, 1 user, load average: 0.28, 0.35, 0.40</code>`
  };
}


// =====================================================================
// 3. Generator Konfigurasi (.env & Run Commands)
// =====================================================================
function initConfigGenerator() {
  const botTokenInput = document.getElementById("cfgBotToken");
  const userIdInput = document.getElementById("cfgUserId");
  const geminiRadio = document.querySelector('input[name="llmProvider"][value="gemini"]');
  const groqRadio = document.querySelector('input[name="llmProvider"][value="groq"]');
  const groupGemini = document.getElementById("groupGemini");
  const groupGroq = document.getElementById("groupGroq");
  const geminiKeyInput = document.getElementById("cfgGeminiKey");
  const geminiModelSelect = document.getElementById("cfgGeminiModel");
  const groqKeyInput = document.getElementById("cfgGroqKey");
  const groqModelSelect = document.getElementById("cfgGroqModel");
  const allowCmdCheck = document.getElementById("cfgAllowCmd");
  const allowScreenshotCheck = document.getElementById("cfgAllowScreenshot");

  const envPreview = document.getElementById("envCodePreview");
  const btnCopyEnv = document.getElementById("btnCopyEnv");
  const btnCopyRun = document.getElementById("btnCopyRun");
  const runCodePreview = document.getElementById("runCodePreview");

  function updateEnv() {
    const isGemini = geminiRadio.checked;
    
    // Toggle UI Groups
    if (isGemini) {
      groupGemini.style.display = "block";
      groupGroq.style.display = "none";
    } else {
      groupGemini.style.display = "none";
      groupGroq.style.display = "block";
    }

    const token = botTokenInput.value.trim() || "1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ_1234567";
    const userIds = userIdInput.value.trim() || "123456789";
    const provider = isGemini ? "gemini" : "groq";
    const geminiKey = geminiKeyInput.value.trim() || "AIzaSy...";
    const geminiModel = geminiModelSelect.value;
    const groqKey = groqKeyInput.value.trim() || "gsk_...";
    const groqModel = groqModelSelect.value;
    const allowCmd = allowCmdCheck.checked ? "True" : "False";
    const allowScreenshot = allowScreenshotCheck.checked ? "True" : "False";

    const content = `# =====================================================================
# File Konfigurasi MiniAgentLite (.env)
# =====================================================================

# 1. Kredensial Telegram Bot & Keamanan
TELEGRAM_BOT_TOKEN=${token}
ALLOWED_USER_IDS=${userIds}

# 2. Mesin LLM Aktif
LLM_PROVIDER=${provider}

# 3. Kredensial Gemini Flash Lite
GEMINI_API_KEY=${geminiKey}
GEMINI_MODEL=${geminiModel}

# 4. Kredensial Groq API
GROQ_API_KEY=${groqKey}
GROQ_MODEL=${groqModel}

# 5. Pengaturan Fitur PC
ENABLE_TERMINAL_COMMANDS=${allowCmd}
ENABLE_SCREENSHOT=${allowScreenshot}`;

    envPreview.textContent = content;
  }

  // Event Listeners
  [botTokenInput, userIdInput, geminiRadio, groqRadio, geminiKeyInput, 
   geminiModelSelect, groqKeyInput, groqModelSelect, allowCmdCheck, allowScreenshotCheck]
   .forEach(el => {
     el.addEventListener("input", updateEnv);
     el.addEventListener("change", updateEnv);
   });

  // Initial update
  updateEnv();

  // Copy Buttons
  btnCopyEnv.addEventListener("click", () => {
    navigator.clipboard.writeText(envPreview.textContent).then(() => {
      btnCopyEnv.textContent = "✅ Tersalin!";
      setTimeout(() => { btnCopyEnv.textContent = "📋 Salin .env"; }, 2000);
    });
  });

  btnCopyRun.addEventListener("click", () => {
    navigator.clipboard.writeText(runCodePreview.textContent).then(() => {
      btnCopyRun.textContent = "✅ Tersalin!";
      setTimeout(() => { btnCopyRun.textContent = "📋 Salin Perintah"; }, 2000);
    });
  });
}

function escapeHtml(str) {
  return str.replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
}
