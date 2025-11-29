"""
LinuxShorts Generator - Project & Settings Preset Manager
Video düzenleme ayarlarını ve projeleri kaydet/yükle
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime

from utils.logger import get_logger

logger = get_logger("LinuxShorts.ProjectPreset")


@dataclass
class VideoSettings:
    """Video düzenleme ayarları"""
    # Transform
    scale: float = 100.0
    pos_x: int = 0
    pos_y: int = 0
    
    # Arka plan
    bg_mode: str = "blur"  # black, blur, gradient, color
    bg_blur_strength: int = 25
    bg_color: str = "#1a1a2e"
    bg_gradient_start: str = "#1a1a2e"
    bg_gradient_end: str = "#16213e"
    
    # Kalite
    crf: int = 23
    preset: str = "medium"
    
    # Overlay
    show_safe_zone: bool = True
    show_grid: bool = False
    show_center_lines: bool = True
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'VideoSettings':
        # Sadece tanımlı alanları al
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)


@dataclass
class ProjectData:
    """Proje verisi"""
    name: str
    video_path: str = ""
    
    # Zaman
    start_time: float = 0.0
    duration: float = 60.0
    
    # Ayarlar
    settings: VideoSettings = field(default_factory=VideoSettings)
    
    # Meta
    created_at: str = ""
    modified_at: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Thumbnail
    thumbnail_text: str = ""
    thumbnail_style: str = "default"
    
    # SEO
    seo_title: str = ""
    seo_description: str = ""
    seo_hashtags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.modified_at:
            self.modified_at = self.created_at
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['settings'] = self.settings.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProjectData':
        settings_data = data.pop('settings', {})
        settings = VideoSettings.from_dict(settings_data)
        
        # Sadece tanımlı alanları al
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(settings=settings, **filtered)


@dataclass  
class SettingsPreset:
    """Ayar preset'i - sadece settings, video bağımsız"""
    name: str
    description: str = ""
    category: str = "Genel"  # Genel, TikTok, YouTube, Instagram
    settings: VideoSettings = field(default_factory=VideoSettings)
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "settings": self.settings.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SettingsPreset':
        settings_data = data.pop('settings', {})
        settings = VideoSettings.from_dict(settings_data)
        return cls(settings=settings, **data)


# Hazır preset'ler
BUILTIN_PRESETS = {
    "default": SettingsPreset(
        name="Varsayılan",
        description="Standart ayarlar",
        category="Genel",
        settings=VideoSettings()
    ),
    "tiktok_blur": SettingsPreset(
        name="TikTok Blur",
        description="TikTok tarzı blur arka plan",
        category="TikTok",
        settings=VideoSettings(
            scale=100,
            bg_mode="blur",
            bg_blur_strength=30,
            crf=23,
            preset="fast"
        )
    ),
    "youtube_clean": SettingsPreset(
        name="YouTube Temiz",
        description="Siyah arka plan, yüksek kalite",
        category="YouTube",
        settings=VideoSettings(
            scale=100,
            bg_mode="black",
            crf=20,
            preset="medium"
        )
    ),
    "zoom_focus": SettingsPreset(
        name="Zoom Odak",
        description="Yakınlaştırılmış, odaklanmış görünüm",
        category="Genel",
        settings=VideoSettings(
            scale=150,
            bg_mode="blur",
            bg_blur_strength=40,
            crf=22
        )
    ),
    "gradient_pro": SettingsPreset(
        name="Gradient Pro",
        description="Profesyonel gradient arka plan",
        category="YouTube",
        settings=VideoSettings(
            scale=100,
            bg_mode="gradient",
            bg_gradient_start="#667eea",
            bg_gradient_end="#764ba2",
            crf=21,
            preset="slow"
        )
    ),
    "instagram_vibrant": SettingsPreset(
        name="Instagram Canlı",
        description="Canlı renkli Instagram tarzı",
        category="Instagram",
        settings=VideoSettings(
            scale=110,
            bg_mode="gradient",
            bg_gradient_start="#f093fb",
            bg_gradient_end="#f5576c",
            crf=22
        )
    ),
    "terminal_dark": SettingsPreset(
        name="Terminal Karanlık",
        description="Terminal ekranı için optimize",
        category="Genel",
        settings=VideoSettings(
            scale=120,
            bg_mode="color",
            bg_color="#0d1117",
            crf=20,
            preset="slow"
        )
    ),
    "fast_export": SettingsPreset(
        name="Hızlı Export",
        description="Düşük kalite, hızlı render",
        category="Genel",
        settings=VideoSettings(
            crf=28,
            preset="ultrafast"
        )
    ),
    "high_quality": SettingsPreset(
        name="Yüksek Kalite",
        description="Maximum kalite, yavaş render",
        category="Genel",
        settings=VideoSettings(
            crf=18,
            preset="slow"
        )
    ),
}


class ProjectPresetManager:
    """Proje ve ayar preset yöneticisi"""
    
    PROJECT_EXTENSION = ".lsp"  # LinuxShorts Project
    PRESET_EXTENSION = ".lspreset"
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Args:
            base_dir: Temel dizin (None ise ~/.linuxshorts kullanılır)
        """
        if base_dir is None:
            base_dir = Path.home() / ".linuxshorts"
        
        self.base_dir = base_dir
        self.projects_dir = base_dir / "projects"
        self.presets_dir = base_dir / "presets"
        
        # Dizinleri oluştur
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.presets_dir.mkdir(parents=True, exist_ok=True)
        
        # Önbellek
        self._presets_cache: Dict[str, SettingsPreset] = {}
        self._load_custom_presets()
    
    def _load_custom_presets(self):
        """Özel preset'leri yükle"""
        for preset_file in self.presets_dir.glob(f"*{self.PRESET_EXTENSION}"):
            try:
                with open(preset_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                preset = SettingsPreset.from_dict(data)
                self._presets_cache[preset.name] = preset
            except Exception as e:
                logger.error(f"Preset yükleme hatası: {preset_file}: {e}")
    
    # ==========================================
    # PRESET METHODS
    # ==========================================
    
    def get_all_presets(self) -> Dict[str, SettingsPreset]:
        """Tüm preset'leri döndür (built-in + custom)"""
        all_presets = dict(BUILTIN_PRESETS)
        all_presets.update(self._presets_cache)
        return all_presets
    
    def get_preset(self, name: str) -> Optional[SettingsPreset]:
        """Preset getir"""
        if name in BUILTIN_PRESETS:
            return BUILTIN_PRESETS[name]
        return self._presets_cache.get(name)
    
    def get_presets_by_category(self, category: str) -> Dict[str, SettingsPreset]:
        """Kategoriye göre preset'leri getir"""
        all_presets = self.get_all_presets()
        return {
            name: preset
            for name, preset in all_presets.items()
            if preset.category == category
        }
    
    def get_categories(self) -> List[str]:
        """Tüm kategorileri getir"""
        categories = set()
        for preset in self.get_all_presets().values():
            categories.add(preset.category)
        return sorted(list(categories))
    
    def save_preset(
        self,
        name: str,
        settings: VideoSettings,
        description: str = "",
        category: str = "Özel"
    ) -> bool:
        """Yeni preset kaydet"""
        try:
            preset = SettingsPreset(
                name=name,
                description=description,
                category=category,
                settings=settings
            )
            
            file_path = self.presets_dir / f"{name}{self.PRESET_EXTENSION}"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(preset.to_dict(), f, indent=2, ensure_ascii=False)
            
            self._presets_cache[name] = preset
            logger.info(f"Preset kaydedildi: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Preset kaydetme hatası: {e}")
            return False
    
    def delete_preset(self, name: str) -> bool:
        """Preset sil (sadece custom)"""
        if name in BUILTIN_PRESETS:
            logger.warning(f"Yerleşik preset silinemez: {name}")
            return False
        
        try:
            file_path = self.presets_dir / f"{name}{self.PRESET_EXTENSION}"
            if file_path.exists():
                file_path.unlink()
            
            if name in self._presets_cache:
                del self._presets_cache[name]
            
            logger.info(f"Preset silindi: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Preset silme hatası: {e}")
            return False
    
    # ==========================================
    # PROJECT METHODS
    # ==========================================
    
    def save_project(
        self,
        project: ProjectData,
        file_path: Optional[Path] = None
    ) -> Optional[Path]:
        """Proje kaydet"""
        try:
            # Güncelleme zamanı
            project.modified_at = datetime.now().isoformat()
            
            # Dosya yolu
            if file_path is None:
                safe_name = "".join(c for c in project.name if c.isalnum() or c in "- _")
                file_path = self.projects_dir / f"{safe_name}{self.PROJECT_EXTENSION}"
            
            # Kaydet
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Proje kaydedildi: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Proje kaydetme hatası: {e}")
            return None
    
    def load_project(self, file_path: Path) -> Optional[ProjectData]:
        """Proje yükle"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            project = ProjectData.from_dict(data)
            logger.info(f"Proje yüklendi: {file_path}")
            return project
            
        except Exception as e:
            logger.error(f"Proje yükleme hatası: {e}")
            return None
    
    def get_recent_projects(self, limit: int = 10) -> List[Dict]:
        """Son projeleri getir"""
        projects = []
        
        for project_file in self.projects_dir.glob(f"*{self.PROJECT_EXTENSION}"):
            try:
                with open(project_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                projects.append({
                    "path": project_file,
                    "name": data.get("name", project_file.stem),
                    "modified_at": data.get("modified_at", ""),
                    "video_path": data.get("video_path", ""),
                    "description": data.get("description", "")
                })
            except:
                continue
        
        # Tarihe göre sırala
        projects.sort(key=lambda p: p["modified_at"], reverse=True)
        
        return projects[:limit]
    
    def delete_project(self, file_path: Path) -> bool:
        """Proje sil"""
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Proje silindi: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Proje silme hatası: {e}")
            return False
    
    def export_project_settings(self, project: ProjectData) -> Dict:
        """Proje ayarlarını export et (paylaşım için)"""
        return {
            "type": "linuxshorts_settings",
            "version": "1.0",
            "settings": project.settings.to_dict(),
            "thumbnail_style": project.thumbnail_style,
            "exported_at": datetime.now().isoformat()
        }
    
    def import_settings_to_project(
        self,
        project: ProjectData,
        settings_data: Dict
    ) -> ProjectData:
        """Ayarları projeye import et"""
        if settings_data.get("type") != "linuxshorts_settings":
            raise ValueError("Geçersiz ayar dosyası formatı")
        
        project.settings = VideoSettings.from_dict(settings_data.get("settings", {}))
        if "thumbnail_style" in settings_data:
            project.thumbnail_style = settings_data["thumbnail_style"]
        
        return project


# Global instance
_manager: Optional[ProjectPresetManager] = None


def get_preset_manager(base_dir: Optional[Path] = None) -> ProjectPresetManager:
    """Global preset manager instance"""
    global _manager
    if _manager is None:
        _manager = ProjectPresetManager(base_dir)
    return _manager


def get_settings_from_preset(preset_name: str) -> Optional[VideoSettings]:
    """Preset'ten ayarları al (kısa yol)"""
    manager = get_preset_manager()
    preset = manager.get_preset(preset_name)
    if preset:
        return preset.settings
    return None
