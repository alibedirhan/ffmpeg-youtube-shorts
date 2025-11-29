"""
LinuxShorts Generator - Logging Sistemi
Detaylı hata yakalama ve log yönetimi
"""

import logging
import sys
import traceback
from pathlib import Path
from datetime import datetime
from functools import wraps


class ColoredFormatter(logging.Formatter):
    """Renkli terminal log formatter"""
    
    # ANSI renk kodları
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # Renk ekle
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        
        # İkon ekle
        icons = {
            'DEBUG': '🔍',
            'INFO': '✓',
            'WARNING': '⚠️',
            'ERROR': '✗',
            'CRITICAL': '💥'
        }
        record.msg = f"{icons.get(record.levelname.strip(), '')} {record.msg}"
        
        return super().format(record)


def setup_logger(name: str = "LinuxShorts", log_file: str = None, level=logging.DEBUG):
    """
    Logger'ı yapılandırır
    
    Args:
        name: Logger adı
        log_file: Log dosyası yolu (None ise sadece console)
        level: Log seviyesi
        
    Returns:
        Yapılandırılmış logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Mevcut handler'ları temizle
    logger.handlers = []
    
    # Console handler (renkli)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (detaylı)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def log_exception(logger):
    """
    Decorator: Fonksiyon hatalarını loglar
    
    Usage:
        @log_exception(logger)
        def my_function():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Hata: {func.__name__}() içinde: {str(e)}")
                logger.debug(f"Traceback:\n{traceback.format_exc()}")
                raise
        return wrapper
    return decorator


def log_function_call(logger, log_args=False):
    """
    Decorator: Fonksiyon çağrılarını loglar
    
    Usage:
        @log_function_call(logger, log_args=True)
        def my_function(x, y):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if log_args:
                logger.debug(f"Çağrılıyor: {func.__name__}(args={args}, kwargs={kwargs})")
            else:
                logger.debug(f"Çağrılıyor: {func.__name__}()")
            
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Tamamlandı: {func.__name__}()")
                return result
            except Exception as e:
                logger.error(f"Hata: {func.__name__}() - {str(e)}")
                raise
        return wrapper
    return decorator


class ExceptionLogger:
    """Global exception handler"""
    
    def __init__(self, logger):
        self.logger = logger
        
    def __call__(self, exc_type, exc_value, exc_traceback):
        """Yakalanmamış exception'ları logla"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        self.logger.critical("="*70)
        self.logger.critical("💥 YAKALANMAMIŞ İSTİSNA!")
        self.logger.critical("="*70)
        self.logger.critical(f"Tip: {exc_type.__name__}")
        self.logger.critical(f"Mesaj: {exc_value}")
        self.logger.critical("")
        self.logger.critical("Traceback:")
        
        # Traceback'i satır satır logla
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        for line in tb_lines:
            for subline in line.strip().split('\n'):
                self.logger.critical(f"  {subline}")
        
        self.logger.critical("="*70)


# Global logger instance
_global_logger = None


def get_logger(name: str = "LinuxShorts") -> logging.Logger:
    """Global logger'ı döndürür"""
    global _global_logger
    
    if _global_logger is None:
        # Log dizini
        log_dir = Path.home() / ".linuxshorts" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Log dosyası adı (timestamp ile)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"linuxshorts_{timestamp}.log"
        
        # Logger'ı kur
        _global_logger = setup_logger(name, str(log_file))
        
        # Global exception handler'ı kur
        sys.excepthook = ExceptionLogger(_global_logger)
        
        _global_logger.info(f"Logger başlatıldı. Log dosyası: {log_file}")
    
    return _global_logger


# Test kodu
if __name__ == "__main__":
    logger = get_logger()
    
    logger.debug("Bu bir debug mesajı")
    logger.info("Bu bir info mesajı")
    logger.warning("Bu bir warning mesajı")
    logger.error("Bu bir error mesajı")
    
    # Exception test
    try:
        x = 1 / 0
    except Exception as e:
        logger.exception("Bir hata oluştu!")
    
    print("\n✅ Logger test başarılı!")
