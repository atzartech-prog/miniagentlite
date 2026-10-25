#!/usr/bin/env python3
"""
MiniAgentLite - Agen Ringan & Cepat Pengendali PC via Telegram
Mendukung Gemini Flash Lite & Groq API dengan Fitur Tool Calling
"""

import os
import sys
import json
import time
import logging
import urllib.request
import urllib.error
import urllib.parse
from typing import Dict, Any, List, Optional

# Load tools modul
import tools

# Setup logging
logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("MiniAgentLite")

# Coba muat python-dotenv jika ada
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Membaca file .env manual secara sederhana jika dotenv belum diinstal
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip())

# Konfigurasi dari Environment
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
ALLOWED_USER_IDS = [
    int(x.strip()) for x in os.getenv("ALLOWED_USER_IDS", "").split(",") if x.strip().isdigit()
]
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

SYSTEM_INSTRUCTION = (
    "Kamu adalah MiniAgentLite, asisten pribadi AI yang cerdas, cepat, dan ramah yang bertugas "
    "mengendalikan dan memantau PC pengguna melalui perintah di Telegram.\n"
    "Kamu memiliki tangan dan kaki digital (Tool Calling) untuk berinteraksi langsung dengan sistem PC:\n"
    "- get_system_status: Untuk memeriksa status CPU, RAM, Disk, Baterai, dan Uptime.\n"
    "- take_screenshot: Untuk mengambil foto tangkapan layar saat ini.\n"
    "- execute_command: Untuk menjalankan perintah terminal/cmd (misal: cek file, cek servis, dsb).\n"
    "- open_application_or_url: Untuk membuka URL website di browser atau membuka aplikasi.\n"
    "- set_volume: Untuk mengubah volume speaker PC (0-100).\n"
    "- send_desktop_notification: Untuk memunculkan notifikasi pop-up di layar PC.\n"
    "Gunakan tools tersebut saat diminta oleh pengguna. Berikan jawaban yang ringkas, jelas, dan informatif dalam bahasa Indonesia."
)


# =====================================================================
# Modul Komunikasi Telegram Bot API (Native HTTP - Tanpa Overhead)
# =====================================================================

class TelegramClient:
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"

    def _post(self, endpoint: str, data: dict) -> dict:
        url = f"{self.base_url}/{endpoint}"
        req_data = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=req_data,
            headers={"Content-Type": "application/json", "User-Agent": "MiniAgentLite/1.0"}
        )
        try:
            with urllib.request.urlopen(req, timeout=40) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8")
            logger.error(f"Telegram API HTTP Error ({e.code}): {err_msg}")
            return {"ok": False, "description": err_msg}
        except Exception as e:
            logger.error(f"Telegram Request Error: {e}")
            return {"ok": False, "description": str(e)}

    def get_me(self) -> dict:
        return self._post("getMe", {})

    def get_updates(self, offset: Optional[int] = None, timeout: int = 25) -> list:
        payload = {"timeout": timeout}
        if offset is not None:
            payload["offset"] = offset
        res = self._post("getUpdates", payload)
        if res.get("ok"):
            return res.get("result", [])
        return []

    def send_chat_action(self, chat_id: int, action: str = "typing"):
        self._post("sendChatAction", {"chat_id": chat_id, "action": action})

    def send_message(self, chat_id: int, text: str, parse_mode: Optional[str] = "Markdown"):
        payload = {
            "chat_id": chat_id,
            "text": text,
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode
        res = self._post("sendMessage", payload)
        # Jika markdown parsing gagal, fallback kirim plain text
        if not res.get("ok") and parse_mode:
            payload.pop("parse_mode")
            self._post("sendMessage", payload)

    def send_photo(self, chat_id: int, file_path: str, caption: str = ""):
        """Mengirim file foto ke Telegram menggunakan multipart/form-data."""
        url = f"{self.base_url}/sendPhoto"
        boundary = f"----MiniAgentBoundary{int(time.time())}"
        
        try:
            with open(file_path, "rb") as f:
                file_bytes = f.read()

            body = bytearray()
            # chat_id field
            body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"chat_id\"\r\n\r\n{chat_id}\r\n".encode("utf-8"))
            # caption field
            if caption:
                body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"caption\"\r\n\r\n{caption}\r\n".encode("utf-8"))
            # photo field
            filename = os.path.basename(file_path)
            body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"photo\"; filename=\"{filename}\"\r\nContent-Type: image/png\r\n\r\n".encode("utf-8"))
            body.extend(file_bytes)
            body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))

            req = urllib.request.Request(
                url,
                data=body,
                headers={
                    "Content-Type": f"multipart/form-data; boundary={boundary}",
                    "User-Agent": "MiniAgentLite/1.0"
                }
            )
            with urllib.request.urlopen(req, timeout=40) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            logger.error(f"Gagal mengirim foto ke Telegram: {e}")
            self.send_message(chat_id, f"⚠️ Gagal mengirim foto screenshot: {str(e)}")


# =====================================================================
# Modul LLM: Groq & Gemini Flash Lite
# =====================================================================

class LLMHandler:
    def __init__(self, provider: str):
        self.provider = provider

    def call_groq(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Panggilan ke Groq API (Format OpenAI Chat Completions)."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": GROQ_MODEL,
            "messages": messages,
            "tools": tools.TOOL_DEFINITIONS_OPENAI,
            "tool_choice": "auto",
            "temperature": 0.2
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]

    def call_gemini(self, user_prompt: str, history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Panggilan ke Google Gemini REST API v1beta."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
        
        # Konversi tools definisi ke format Gemini functionDeclarations
        gemini_tools = [{
            "functionDeclarations": [
                {
                    "name": t["function"]["name"],
                    "description": t["function"]["description"],
                    "parameters": t["function"]["parameters"]
                }
                for t in tools.TOOL_DEFINITIONS_OPENAI
            ]
        }]

        contents = []
        if history:
            contents.extend(history)
        contents.append({"role": "user", "parts": [{"text": user_prompt}]})

        payload = {
            "systemInstruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
            "contents": contents,
            "tools": gemini_tools
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            candidate = data.get("candidates", [{}])[0].get("content", {})
            return candidate


# =====================================================================
# Logika Utama Agen: Eksekusi Tool Calling & Respon
# =====================================================================

def process_with_groq(telegram: TelegramClient, chat_id: int, user_text: str):
    llm = LLMHandler("groq")
    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        {"role": "user", "content": user_text}
    ]

    telegram.send_chat_action(chat_id, "typing")
    try:
        assistant_msg = llm.call_groq(messages)
    except Exception as e:
        logger.error(f"Error calling Groq: {e}")
        telegram.send_message(chat_id, f"❌ Terjadi kesalahan pada Groq API: {str(e)}")
        return

    # Periksa apakah model meminta tool call
    tool_calls = assistant_msg.get("tool_calls")
    if not tool_calls:
        # Respon teks biasa
        reply_content = assistant_msg.get("content", "Maaf, saya tidak dapat memahami permintaan Anda.")
        telegram.send_message(chat_id, reply_content)
        return

    # Model meminta satu atau beberapa tool call
    messages.append(assistant_msg)
    screenshot_to_send = None

    for tool_call in tool_calls:
        fn_name = tool_call["function"]["name"]
        fn_args_raw = tool_call["function"].get("arguments", "{}")
        try:
            fn_args = json.loads(fn_args_raw) if isinstance(fn_args_raw, str) else fn_args_raw
        except Exception:
            fn_args = {}

        logger.info(f"⚡ Menjalankan Tool Calling: {fn_name}({fn_args})")
        telegram.send_chat_action(chat_id, "typing")
        
        # Eksekusi tool
        result = tools.dispatch_tool(fn_name, fn_args)

        # Cek apakah ini tool screenshot
        if fn_name == "take_screenshot" and result.get("status") == "success":
            screenshot_to_send = result.get("file_path")

        # Masukkan hasil tool ke history pesan
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "name": fn_name,
            "content": json.dumps(result, ensure_ascii=False)
        })

    # Kirim kembali ke model untuk ringkasan akhir
    try:
        final_msg = llm.call_groq(messages)
        final_text = final_msg.get("content", "Tindakan telah berhasil diselesaikan.")
    except Exception:
        final_text = "Perintah telah dieksekusi di PC."

    if screenshot_to_send and os.path.exists(screenshot_to_send):
        telegram.send_photo(chat_id, screenshot_to_send, caption=final_text[:1024])
    else:
        telegram.send_message(chat_id, final_text)


def process_with_gemini(telegram: TelegramClient, chat_id: int, user_text: str):
    llm = LLMHandler("gemini")
    telegram.send_chat_action(chat_id, "typing")

    try:
        candidate_content = llm.call_gemini(user_text)
    except Exception as e:
        logger.error(f"Error calling Gemini: {e}")
        telegram.send_message(chat_id, f"❌ Terjadi kesalahan pada Gemini Flash Lite API: {str(e)}")
        return

    parts = candidate_content.get("parts", [])
    function_calls = [p["functionCall"] for p in parts if "functionCall" in p]

    # Jika tidak ada function call, kirim respon teks
    if not function_calls:
        text_parts = [p.get("text", "") for p in parts if "text" in p]
        full_text = "".join(text_parts).strip() or "Permintaan diterima."
        telegram.send_message(chat_id, full_text)
        return

    # Model meminta pemanggilan fungsi
    screenshot_to_send = None
    tool_results = []

    for fc in function_calls:
        fn_name = fc.get("name")
        fn_args = fc.get("args", {})

        logger.info(f"⚡ Menjalankan Tool Calling (Gemini): {fn_name}({fn_args})")
        telegram.send_chat_action(chat_id, "typing")
        
        exec_res = tools.dispatch_tool(fn_name, fn_args)

        if fn_name == "take_screenshot" and exec_res.get("status") == "success":
            screenshot_to_send = exec_res.get("file_path")

        tool_results.append({
            "functionResponse": {
                "name": fn_name,
                "response": {"output": exec_res}
            }
        })

    # Kirim kembali hasil tool ke Gemini untuk memperoleh jawaban akhir yang ramah
    history = [
        {"role": "user", "parts": [{"text": user_text}]},
        {"role": "model", "parts": candidate_content.get("parts", [])},
        {"role": "user", "parts": tool_results}
    ]

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "systemInstruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
            "contents": history
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            final_parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            final_text = "".join([p.get("text", "") for p in final_parts if "text" in p]).strip()
    except Exception as e:
        logger.warning(f"Gagal generate final text dari Gemini: {e}")
        final_text = "Perintah di PC berhasil dijalankan."

    if screenshot_to_send and os.path.exists(screenshot_to_send):
        telegram.send_photo(chat_id, screenshot_to_send, caption=final_text[:1024])
    else:
        telegram.send_message(chat_id, final_text or "Selesai dieksekusi.")


# =====================================================================
# Main Loop (Polling Telegram)
# =====================================================================

def main():
    print("""
=====================================================
    🤖 MINI AGENT LITE - PC Controller Telegram Agent
=====================================================
    - Provider : """ + LLM_PROVIDER.upper() + """
    - Keamanan : Whitelist ID Aktif (""" + str(len(ALLOWED_USER_IDS)) + """ User diizinkan)
=====================================================
    """)

    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN belum diset! Silakan edit file .env Anda.")
        sys.exit(1)

    if LLM_PROVIDER == "gemini" and not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY belum diset di .env! Silakan isi terlebih dahulu.")
        sys.exit(1)
    elif LLM_PROVIDER == "groq" and not GROQ_API_KEY:
        logger.error("GROQ_API_KEY belum diset di .env! Silakan isi terlebih dahulu.")
        sys.exit(1)

    telegram = TelegramClient(TELEGRAM_BOT_TOKEN)
    bot_info = telegram.get_me()
    if not bot_info.get("ok"):
        logger.error(f"Gagal menghubungkan bot Telegram: {bot_info.get('description')}")
        sys.exit(1)

    bot_name = bot_info["result"]["first_name"]
    bot_username = bot_info["result"].get("username", "")
    logger.info(f"✅ Bot Terhubung: @{bot_username} ({bot_name})")
    logger.info("Menunggu pesan dari Telegram... (Tekan Ctrl+C untuk berhenti)")

    last_update_id = 0

    while True:
        try:
            updates = telegram.get_updates(offset=last_update_id + 1, timeout=25)
            for upd in updates:
                last_update_id = upd.get("update_id", last_update_id)
                msg = upd.get("message")
                if not msg:
                    continue

                user = msg.get("from", {})
                chat_id = msg.get("chat", {}).get("id")
                user_id = user.get("id")
                user_name = user.get("first_name", "User")
                text = msg.get("text", "").strip()

                if not text:
                    continue

                logger.info(f"Pesan diterima dari @{user.get('username', user_name)} (ID: {user_id}): {text}")

                # Pemeriksaan Keamanan Whitelist User ID
                if ALLOWED_USER_IDS and user_id not in ALLOWED_USER_IDS:
                    logger.warning(f"⛔ Akses Ditolak untuk User ID tidak dikenal: {user_id}")
                    telegram.send_message(
                        chat_id,
                        f"🔒 *Akses Ditolak*\nID Telegram Anda (`{user_id}`) belum didaftarkan di file konfigurasi PC ini.",
                        parse_mode="Markdown"
                    )
                    continue

                # Perintah Start / Bantuan
                if text.lower() in ["/start", "/help", "halo", "hai"]:
                    help_text = (
                        f"👋 Halo *{user_name}*! Saya *MiniAgentLite* yang terhubung langsung ke PC Anda.\n\n"
                        "💡 *Contoh Perintah yang bisa dicoba:*\n"
                        "• _'Berapa sisa RAM, disk, dan baterai sekarang?'_\n"
                        "• _'Ambil screenshot layar PC saya'_\n"
                        "• _'Buka YouTube di browser PC'_\n"
                        "• _'Kecilkan volume speaker ke 30%'_\n"
                        "• _'Munculkan notifikasi: Halo dari Telegram'_\n"
                        "• _'Jalankan perintah cmd/terminal: ping google.com'_\n\n"
                        f"⚙️ Mesin Aktif: `{LLM_PROVIDER.upper()}`"
                    )
                    telegram.send_message(chat_id, help_text)
                    continue

                # Proses pesan dengan LLM
                if LLM_PROVIDER == "groq":
                    process_with_groq(telegram, chat_id, text)
                else:
                    process_with_gemini(telegram, chat_id, text)

        except KeyboardInterrupt:
            logger.info("Bot dihentikan oleh pengguna.")
            break
        except Exception as e:
            logger.error(f"Error loop utama: {e}")
            time.sleep(3)


if __name__ == "__main__":
    main()
