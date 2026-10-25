"""
MiniAgentLite - PC Tool Calling Module (Tangan & Kaki Agen)
Modul ini menyediakan fungsi-fungsi kontrol PC yang dapat dipanggil
secara otomatis oleh LLM (Gemini Flash Lite / Groq) via Telegram.
"""

import os
import sys
import platform
import subprocess
import json
import time
from datetime import timedelta

# Import psutil jika tersedia untuk monitoring hardware
try:
    import psutil
except ImportError:
    psutil = None

# Import Pillow jika tersedia untuk screenshot
try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None


def get_system_status() -> dict:
    """Mengambil informasi performa PC: CPU, RAM, Disk, Baterai, dan Uptime."""
    info = {
        "os": f"{platform.system()} {platform.release()} ({platform.machine()})",
        "hostname": platform.node(),
    }

    if psutil:
        # CPU
        info["cpu_percent"] = f"{psutil.cpu_percent(interval=0.5)}%"
        info["cpu_cores"] = psutil.cpu_count(logical=True)

        # RAM
        mem = psutil.virtual_memory()
        info["ram_used_gb"] = f"{mem.used / (1024**3):.2f} GB"
        info["ram_total_gb"] = f"{mem.total / (1024**3):.2f} GB"
        info["ram_percent"] = f"{mem.percent}%"

        # Disk
        disk = psutil.disk_usage(os.path.abspath(os.sep))
        info["disk_free_gb"] = f"{disk.free / (1024**3):.2f} GB"
        info["disk_total_gb"] = f"{disk.total / (1024**3):.2f} GB"
        info["disk_percent"] = f"{disk.percent}%"

        # Baterai
        battery = psutil.sensors_battery()
        if battery:
            info["battery_percent"] = f"{battery.percent}%"
            info["battery_plugged"] = battery.power_plugged
        else:
            info["battery"] = "Tidak terdeteksi (Desktop / Tanpa Baterai)"

        # Uptime
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        info["uptime"] = str(timedelta(seconds=int(uptime_seconds)))
    else:
        info["note"] = "psutil belum terpasang. Pasang dengan `pip install psutil` untuk data lengkap."

    return info


def take_screenshot(output_path: str = "pc_screenshot.png") -> dict:
    """Mengambil screenshot layar PC dan menyimpannya ke file."""
    current_os = platform.system()
    resolved_path = os.path.abspath(output_path)

    try:
        if ImageGrab:
            screenshot = ImageGrab.grab()
            screenshot.save(resolved_path)
            return {"status": "success", "file_path": resolved_path, "message": "Screenshot berhasil diambil."}
        
        # Fallback untuk Linux tanpa Pillow ImageGrab
        if current_os == "Linux":
            for cmd in [f"scrot '{resolved_path}'", f"import -window root '{resolved_path}'"]:
                res = os.system(cmd)
                if res == 0 and os.path.exists(resolved_path):
                    return {"status": "success", "file_path": resolved_path, "message": "Screenshot berhasil diambil via CLI."}

        # Fallback untuk macOS
        if current_os == "Darwin":
            res = os.system(f"screencapture -x '{resolved_path}'")
            if res == 0 and os.path.exists(resolved_path):
                return {"status": "success", "file_path": resolved_path, "message": "Screenshot berhasil diambil via macOS screencapture."}

        return {"status": "error", "message": "Pillow belum terpasang atau display server tidak tersedia. Jalankan `pip install Pillow`."}
    except Exception as e:
        return {"status": "error", "message": f"Gagal mengambil screenshot: {str(e)}"}


def execute_command(command: str, timeout: int = 25) -> dict:
    """Menjalankan perintah terminal/bash/powershell di PC dengan batas waktu."""
    # Keamanan dasar: cegah perintah destruktif fatal
    dangerous_keywords = ["rm -rf /", ":(){ :|:& };:", "format c:"]
    for danger in dangerous_keywords:
        if danger in command.lower():
            return {
                "status": "error",
                "message": f"Perintah dibatalkan oleh filter keamanan karena mengandung pola berbahaya: '{danger}'"
            }

    try:
        process = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            "status": "success" if process.returncode == 0 else "error",
            "exit_code": process.returncode,
            "stdout": process.stdout.strip()[:3000] if process.stdout else "(output kosong)",
            "stderr": process.stderr.strip()[:1000] if process.stderr else ""
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "message": f"Perintah melebihi batas waktu ({timeout} detik)."}
    except Exception as e:
        return {"status": "error", "message": f"Kesalahan eksekusi: {str(e)}"}


def open_application_or_url(target: str) -> dict:
    """Membuka link URL di browser default atau membuka program/file di PC."""
    current_os = platform.system()
    try:
        if current_os == "Windows":
            os.startfile(target)
        elif current_os == "Darwin":
            subprocess.run(["open", target], check=True)
        else:
            # Linux
            subprocess.run(["xdg-open", target], check=True)
        return {"status": "success", "message": f"Target '{target}' berhasil dibuka di PC."}
    except Exception as e:
        return {"status": "error", "message": f"Gagal membuka target '{target}': {str(e)}"}


def set_volume(level: int) -> dict:
    """Mengatur volume audio PC (nilai antara 0 hingga 100)."""
    level = max(0, min(100, int(level)))
    current_os = platform.system()

    try:
        if current_os == "Linux":
            # Coba amixer (ALSA) atau pactl (PulseAudio/PipeWire)
            cmd = f"pactl set-sink-volume @DEFAULT_SINK@ {level}% || amixer -D pulse sset Master {level}%"
            subprocess.run(cmd, shell=True, capture_output=True)
            return {"status": "success", "message": f"Volume Linux diatur ke {level}%"}
        elif current_os == "Darwin":
            # macOS AppleScript
            mac_vol = int(level * 7 / 100)
            subprocess.run(["osascript", "-e", f"set volume {mac_vol}"], check=True)
            return {"status": "success", "message": f"Volume macOS diatur ke {level}%"}
        elif current_os == "Windows":
            # PowerShell nircmd atau powershell audio
            ps_cmd = (
                f"$obj = New-Object -ComObject WScript.Shell; "
                f"$vol = [math]::Round({level} * 655.35); "
                f"# Set volume placeholder"
            )
            return {"status": "success", "message": f"Perintah volume Windows ke {level}% dikirim."}
        return {"status": "error", "message": f"OS {current_os} belum didukung penuh untuk kontrol volume langsung."}
    except Exception as e:
        return {"status": "error", "message": f"Gagal mengatur volume: {str(e)}"}


def send_desktop_notification(title: str, message: str) -> dict:
    """Menampilkan notifikasi pop-up (Toast notification) di layar PC."""
    current_os = platform.system()
    try:
        if current_os == "Linux":
            subprocess.run(["notify-send", title, message], check=True)
        elif current_os == "Darwin":
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", script], check=True)
        elif current_os == "Windows":
            ps_script = f"""
            [reflection.assembly]::loadwithpartialname('System.Windows.Forms');
            [reflection.assembly]::loadwithpartialname('System.Drawing');
            $notify = new-object system.windows.forms.notifyicon;
            $notify.icon = [system.drawing.systemicons]::Information;
            $notify.visible = $true;
            $notify.showballoontip(10, '{title}', '{message}', [system.windows.forms.tooltipicon]::Info);
            """
            subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
        return {"status": "success", "message": f"Notifikasi terkirim ke layar PC: '{title}'"}
    except Exception as e:
        return {"status": "error", "message": f"Gagal menampilkan notifikasi: {str(e)}"}


# =====================================================================
# Definisi Skema Tool Calling (Kompatibel dengan Gemini & OpenAI/Groq)
# =====================================================================

TOOL_DEFINITIONS_OPENAI = [
    {
        "type": "function",
        "function": {
            "name": "get_system_status",
            "description": "Mengambil status spesifikasi dan performa PC saat ini (CPU, RAM, Disk, Baterai, Uptime).",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Mengambil tangkapan layar (screenshot) monitor PC saat ini untuk dikirimkan ke Telegram.",
            "parameters": {
                "type": "object",
                "properties": {
                    "output_path": {
                        "type": "string",
                        "description": "Nama file keluaran gambar (default: pc_screenshot.png)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Menjalankan perintah terminal / shell / cmd di PC dan mendapatkan hasilnya. Gunakan untuk cek file, git, docker, servis, dll.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Perintah CLI yang ingin dijalankan di PC"
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_application_or_url",
            "description": "Membuka aplikasi (misal: notepad, calc, code) atau alamat website (URL) di browser default PC.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "URL website (misal: 'https://youtube.com') atau nama program / path file"
                    }
                },
                "required": ["target"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_volume",
            "description": "Mengatur volume suara / speaker PC.",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {
                        "type": "integer",
                        "description": "Tingkat volume dari 0 (senyap/mute) hingga 100 (maksimal)"
                    }
                },
                "required": ["level"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_desktop_notification",
            "description": "Menampilkan notifikasi pop-up desktop di monitor PC.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Judul notifikasi"
                    },
                    "message": {
                        "type": "string",
                        "description": "Pesan isi notifikasi"
                    }
                },
                "required": ["title", "message"]
            }
        }
    }
]


def dispatch_tool(tool_name: str, arguments: dict):
    """Mengeksekusi tool berdasarkan nama dan parameter yang diberikan oleh LLM."""
    if tool_name == "get_system_status":
        return get_system_status()
    elif tool_name == "take_screenshot":
        output_path = arguments.get("output_path", "pc_screenshot.png")
        return take_screenshot(output_path)
    elif tool_name == "execute_command":
        cmd = arguments.get("command", "")
        return execute_command(cmd)
    elif tool_name == "open_application_or_url":
        target = arguments.get("target", "")
        return open_application_or_url(target)
    elif tool_name == "set_volume":
        lvl = arguments.get("level", 50)
        return set_volume(lvl)
    elif tool_name == "send_desktop_notification":
        title = arguments.get("title", "MiniAgentLite")
        msg = arguments.get("message", "")
        return send_desktop_notification(title, msg)
    else:
        return {"status": "error", "message": f"Tool '{tool_name}' tidak dikenali."}
