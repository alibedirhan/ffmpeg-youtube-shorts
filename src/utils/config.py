"""
LinuxShorts Generator - Konfigürasyon Dosyası
"""

import os
from pathlib import Path

# Uygulama Bilgileri
APP_NAME = "LinuxShorts Generator"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Ali Bedirhan"
APP_DESCRIPTION = "FFmpeg ile YouTube Shorts üretici"

# Dizinler
BASE_DIR = Path(__file__).parent.parent.parent
PRESETS_DIR = BASE_DIR / "presets"
OUTPUT_DIR = Path.home() / "Videos" / "Shorts"

# Video Ayarları
VIDEO_SETTINGS = {
    "width": 1080,
    "height": 1920,
    "aspect_ratio": "9:16",
    "codec": "libx264",
    "audio_codec": "aac",
    "crf": 23,  # Kalite (18-28 arası, düşük = yüksek kalite)
    "preset": "medium",  # ultrafast, fast, medium, slow, veryslow
}

# FFmpeg Ayarları
FFMPEG_PATH = "ffmpeg"  # System PATH'te varsa "ffmpeg" yeterli

# GUI Ayarları
THEME = "dark-blue"  # dark-blue, green, dark-green
APPEARANCE_MODE = "dark"  # light, dark, system

# Preset Kategorileri
PRESET_CATEGORIES = [
    "Genel",
    "Linux Paket Yönetimi",
    "Terminal Komutları",
    "Sistem Yönetimi",
]

# Dosya Uzantıları
SUPPORTED_VIDEO_FORMATS = [
    ("Video Dosyaları", "*.mp4 *.avi *.mkv *.mov *.flv *.wmv"),
    ("Tüm Dosyalar", "*.*")
]

# Hata Mesajları
ERROR_MESSAGES = {
    "no_video": "Lütfen bir video dosyası seçin!",
    "invalid_time": "Geçersiz zaman aralığı!",
    "ffmpeg_not_found": "FFmpeg bulunamadı! Lütfen FFmpeg'i kurun.",
    "export_failed": "Video oluşturulurken hata oluştu!",
    "no_preset_selected": "Lütfen bir preset seçin!",
}

# Başarı Mesajları
SUCCESS_MESSAGES = {
    "export_complete": "Short video başarıyla oluşturuldu!",
    "preset_saved": "Preset başarıyla kaydedildi!",
    "preset_loaded": "Preset yüklendi!",
}

# Output dizinini oluştur
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
