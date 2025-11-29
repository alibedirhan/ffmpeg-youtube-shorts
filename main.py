#!/usr/bin/env python3
"""
LinuxShorts Pro - Professional YouTube Shorts Generator
"""

import sys
from pathlib import Path

# Proje kök dizinini Python path'e ekle
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

from utils.logger import get_logger

logger = get_logger("LinuxShorts.Main")

logger.info("=" * 70)
logger.info("🎬 LinuxShorts Pro Başlatılıyor...")
logger.info("=" * 70)
logger.info(f"📁 Proje: {PROJECT_ROOT}")
logger.info(f"🐍 Python: {sys.version.split()[0]}")
logger.info("")

try:
    from gui.main_window import main
    logger.info("✓ Modüller yüklendi")
    logger.info("🚀 GUI başlatılıyor...")
    main()
    
except KeyboardInterrupt:
    logger.info("\n👋 Kapatıldı")
    sys.exit(0)
    
except ImportError as e:
    logger.critical(f"Import hatası: {e}")
    logger.critical("pip install -r requirements.txt")
    sys.exit(1)
    
except Exception as e:
    logger.critical(f"Hata: {e}")
    logger.exception("Detay:")
    sys.exit(1)
