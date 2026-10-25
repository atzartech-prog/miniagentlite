# ⚡ MiniAgentLite: Agen Ringan & Cepat Pengendali PC via Telegram

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-2CA5E0?logo=telegram)
![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash%20Lite-8E75C2?logo=googlegemini)
![Groq](https://img.shields.io/badge/Groq-Llama%203.3%2070B-F55036?logo=meta)
![License](https://img.shields.io/badge/License-MIT-green)

**Bangun Asisten AI Pribadi dengan "Tangan & Kaki" untuk Mengontrol Komputer Anda dari Smartphone Kapan Saja.**

[🎮 Buka Aplikasi Web & Simulator Interaktif](https://atzartech-prog.github.io/miniagentlite/) &bull; [📖 Panduan Cepat](#-panduan-instalasi-4-langkah-mudah) &bull; [🦾 Katalog Tools](#-katalog-tangan--kaki-tool-calling) &bull; [🔒 Keamanan](#-keamanan--privasi)

</div>

---

## 📌 Apa itu MiniAgentLite?

**MiniAgentLite** adalah framework agen AI ultra-ringan, hemat daya, dan cepat yang dirancang untuk kebutuhan sehari-hari. Berjalan langsung di latar belakang PC (Windows, macOS, Linux) Anda dan terhubung ke **Telegram Bot**. 

Dengan memanfaatkan kecepatan **Google Gemini Flash Lite** atau **Groq Cloud API (Llama 3.3 70B)**, agen ini dapat berpikir dan merespons dalam hitungan milidetik (~300ms) tanpa membebani RAM komputer Anda (< 35 MB).

Dilengkapi dengan kemampuan **Tool Calling (Tangan dan Kaki)**, agen ini bukan sekadar chatbot yang hanya bisa mengobrol, melainkan asisten yang dapat melakukan tindakan fisik di PC Anda secara nyata.

---

## ✨ Fitur Utama

- 🚀 **Super Cepat & Ringan:** Latensi respon secepat kilat (~300ms) menggunakan Gemini 2.5 Flash Lite atau Groq Llama 3.3.
- 📱 **Remote Control via Telegram:** Cukup chat seperti mengobrol dengan teman di Telegram untuk mengontrol PC dari mana saja (tanpa perlu IP publik, port forwarding, atau VPN rumit).
- 🦾 **Tool Calling (Tangan & Kaki Komputer):**
  - 📊 **Cek Hardware:** Pantau persentase CPU, RAM, disk, status baterai laptop, dan uptime.
  - 📸 **Screenshot Instan:** Ambil tangkapan layar monitor dan langsung dikirim ke chat Telegram.
  - 🌐 **Peluncur Web & Aplikasi:** Buka link di browser atau luncurkan aplikasi di desktop secara otomatis.
  - 🔊 **Kontrol Audio:** Ubah volume suara speaker (0-100%).
  - 🔔 **Notifikasi Pop-up:** Kirim notifikasi toast ke layar PC.
  - 💻 **Terminal Shell:** Jalankan perintah CLI (aman dengan filter perintah destruktif).
- 🔒 **Aman (Whitelist User ID):** Hanya akun Telegram pemilik yang dapat memberikan perintah ke PC. Orang asing akan langsung ditolak.
- 🌐 **Web App & Simulator Interaktif:** Termasuk aplikasi web modern (`index.html`) untuk mensimulasikan alur tool calling dan membuat file `.env` secara visual.

---

## 📐 Arsitektur Sistem

```
+------------------+         +----------------------+         +-----------------------+
|  HP Pengguna     |  Chat   |  Telegram Bot API    | Polling |   MiniAgentLite       |
|  (App Telegram)  | ------> |  (Cloud Telegram)    | ------> |   (agent.py di PC)    |
+------------------+         +----------------------+         +-----------+-----------+
                                                                          |
                                                      Kirim Teks + Tools  |  Kembalikan
                                                                          v  Function Call
                                                              +-----------+-----------+
                                                              |  Gemini Flash Lite    |
                                                              |  / Groq Cloud API     |
                                                              +-----------+-----------+
                                                                          |
                                                             Eksekusi     v
                                                      +-------------------------------+
                                                      |  Tangan & Kaki PC (tools.py)  |
                                                      |  - Monitor & Hardware         |
                                                      |  - Screenshot Monitor         |
                                                      |  - Buka Browser / Aplikasi    |
                                                      |  - Audio Volume & Terminal    |
                                                      +-------------------------------+
```

---

## 🚀 Panduan Instalasi (4 Langkah Mudah)

### Langkah 1: Buat Bot Telegram & Catat ID Akun Anda
1. Buka Telegram dan cari bot resmi **[@BotFather](https://t.me/BotFather)**.
2. Kirim perintah `/newbot`, beri nama bot Anda, dan Anda akan menerima **Bot Token HTTP API** (contoh: `7123456789:AAH...`).
3. Buka bot **[@userinfobot](https://t.me/userinfobot)** dan klik Start untuk mengetahui angka **Id** akun Anda (contoh: `123456789`).

### Langkah 2: Dapatkan API Key LLM (100% Gratis)
Pilih salah satu (atau keduanya):
- **Google Gemini Flash Lite:** Dapatkan API Key gratis di [Google AI Studio](https://aistudio.google.com/).
- **Groq Cloud API:** Dapatkan API Key gratis di [Groq Console](https://console.groq.com/keys) (Sangat direkomendasikan karena kecepatan inferensi mencapai 500+ token/detik).

### Langkah 3: Clone Repositori & Pasang Dependencies
Buka terminal (Linux/macOS) atau Command Prompt / PowerShell (Windows):

```bash
# 1. Clone repositori ini
git clone https://github.com/atzartech-prog/miniagentlite.git
cd miniagentlite

# 2. (Opsional tapi disarankan) Buat virtual environment
python -m venv venv
# Linux / macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 3. Install library pendukung
pip install -r requirements.txt
```

### Langkah 4: Buat File `.env` & Jalankan!
Salin template konfigurasi:

```bash
cp config.example.env .env
```

Buka file `.env` dengan text editor (Notepad, VS Code, atau nano), lalu isi:

```ini
# Token dari @BotFather
TELEGRAM_BOT_TOKEN=7123456789:AAHxxxxxxxxxxxxxxxxxxxxxxx

# ID akun Telegram Anda dari @userinfobot (PENTING!)
ALLOWED_USER_IDS=123456789

# Pilih mesin: "gemini" atau "groq"
LLM_PROVIDER=gemini

# Jika memilih gemini:
GEMINI_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxx
GEMINI_MODEL=gemini-2.5-flash-lite

# Jika memilih groq:
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
GROQ_MODEL=llama-3.3-70b-versatile
```

Setelah itu, jalankan agen:

```bash
python agent.py
```

Sekarang buka aplikasi Telegram di HP Anda, kirim pesan ke bot Anda:
> *"Halo! Berapa sisa RAM dan CPU komputer saya sekarang?"*

Agen akan langsung memeriksa kondisi komputer Anda dan memberikan laporannya!

---

## 🦾 Katalog "Tangan & Kaki" (Tool Calling)

| Nama Tool | Fungsi | Contoh Perintah di Telegram | Status Keamanan |
| :--- | :--- | :--- | :---: |
| `get_system_status` | Cek penggunaan CPU, RAM, Disk, Baterai, dan Uptime | *"Cek kondisi PC saya sekarang"* | 🟢 Safe (Read-only) |
| `take_screenshot` | Tangkap layar monitor dan kirim gambar ke chat | *"Tolong fotokan layar PC dong"* | 🟢 Safe (Visual) |
| `open_application_or_url` | Buka alamat web di browser atau buka aplikasi desktop | *"Buka https://github.com di browser"* | 🟢 Safe |
| `set_volume` | Mengatur tingkat kekerasan speaker (0-100%) | *"Kecilkan volume suara ke 20%"* | 🟢 Safe |
| `send_desktop_notification` | Munculkan notifikasi pop-up di layar monitor | *"Munculkan pesan di layar: Waktunya makan"* | 🟢 Safe |
| `execute_command` | Menjalankan perintah terminal / bash / powershell | *"Jalankan: git status"* | 🟡 Power Tool |

---

## 🌐 Menjalankan Aplikasi Web Interaktif

Proyek ini dilengkapi dengan aplikasi showcase interaktif berbasis **HTML5, CSS3, dan Vanilla JS**. 

Aplikasi ini mencakup:
- 🧪 **Live Tool Calling Playground:** Simulator interaktif untuk menguji bagaimana LLM memilih fungsi dan mengeksekusi kontrol PC tanpa perlu menyalakan Telegram.
- ⚙️ **Konfigurator Visual:** Buat file `.env` dan kode perintah dengan satu klik.
- 📊 **Visualisasi Arsitektur:** Diagram interaktif yang menjelaskan peran tiap komponen.

Untuk membukanya:
Cukup buka file `index.html` di browser favorit Anda (Chrome, Firefox, Safari, Edge) langsung tanpa perlu web server!

```bash
# Atau gunakan python simple server jika mau:
python -m http.server 8080
# Buka http://localhost:8080 di browser
```

---

## 🔒 Keamanan & Privasi

1. **Whitelist ID Wajib:** Agen memiliki sistem verifikasi `ALLOWED_USER_IDS`. Hanya akun Telegram Anda yang dapat mengeksekusi perintah. Pesan dari pengguna lain otomatis diabaikan.
2. **Filter Kata Kunci Berbahaya:** Modul terminal memiliki proteksi terhadap perintah perusak seperti `rm -rf /` atau format harddisk.
3. **Komunikasi Langsung:** Tidak ada server pihak ketiga perantara selain Telegram dan API AI resmi (Google / Groq).

---

## 🛠️ Menjalankan Agen Otomatis di Background (Linux / Windows)

### Di Linux (systemd service)
Buat file service di `/etc/systemd/system/miniagent.service`:

```ini
[Unit]
Description=MiniAgentLite Telegram PC Controller
After=network.target

[Service]
Type=simple
User=username_anda
WorkingDirectory=/path/ke/miniagentlite
ExecStart=/path/ke/miniagentlite/venv/bin/python agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Lalu aktifkan:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now miniagent
```

### Di Windows
Anda bisa membuat shortcut file `.bat` di folder `Startup` (`Win + R` -> ketik `shell:startup`):

```bat
@echo off
cd /d "C:\path\ke\miniagentlite"
python agent.py
pause
```

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE). Bebas digunakan, dipelajari, dimodifikasi, dan dikembangkan untuk keperluan pribadi maupun komersial.
