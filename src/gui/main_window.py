"""
LinuxShorts Pro v2.0 - Modern GUI
Tamamen yeniden tasarlanmış, kullanıcı dostu arayüz
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageEnhance
from pathlib import Path
from typing import Optional, List, Callable
import threading
import sys
import os

# OpenCV import kontrolü
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    np = None

# Path ayarları
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.logger import get_logger
from utils.config import (
    APP_NAME, APPEARANCE_MODE, THEME, SUPPORTED_VIDEO_FORMATS,
    OUTPUT_DIR, PRESETS_DIR
)

logger = get_logger("LinuxShorts.GUI")

# ============================================================
# RENK TEMASi
# ============================================================
COLORS = {
    "bg_dark": "#1a1a2e",
    "bg_card": "#16213e",
    "bg_hover": "#1f3460",
    "accent": "#e94560",
    "accent_hover": "#ff6b6b",
    "success": "#00d26a",
    "warning": "#ffc107",
    "text": "#ffffff",
    "text_dim": "#a0a0a0",
    "border": "#2a2a4a"
}


# ============================================================
# YARDIMCI WIDGET'LAR
# ============================================================

class ModernCard(ctk.CTkFrame):
    """Modern kart widget'ı"""
    
    def __init__(self, parent, title: str = "", icon: str = "", **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_card"], corner_radius=12, **kwargs)
        
        if title:
            header = ctk.CTkFrame(self, fg_color="transparent")
            header.pack(fill="x", padx=15, pady=(15, 10))
            
            ctk.CTkLabel(
                header,
                text=f"{icon} {title}" if icon else title,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLORS["text"]
            ).pack(side="left")
        
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    
    def get_content(self) -> ctk.CTkFrame:
        return self.content


class ModernButton(ctk.CTkButton):
    """Modern buton widget'ı"""
    
    def __init__(self, parent, text: str, icon: str = "", variant: str = "primary", **kwargs):
        colors = {
            "primary": (COLORS["accent"], COLORS["accent_hover"]),
            "secondary": (COLORS["bg_hover"], "#2a4a7a"),
            "success": (COLORS["success"], "#00ff7f"),
            "ghost": ("transparent", COLORS["bg_hover"])
        }
        
        fg, hover = colors.get(variant, colors["primary"])
        
        display_text = f"{icon} {text}" if icon else text
        
        # Font parametresi kwargs'dan al, yoksa varsayılan kullan
        font = kwargs.pop("font", ctk.CTkFont(size=13))
        
        super().__init__(
            parent,
            text=display_text,
            fg_color=fg,
            hover_color=hover,
            corner_radius=8,
            font=font,
            **kwargs
        )


class ModernSlider(ctk.CTkFrame):
    """Slider with label and value display"""
    
    def __init__(self, parent, label: str, from_: float, to: float, 
                 default: float = None, unit: str = "", command: Callable = None):
        super().__init__(parent, fg_color="transparent")
        
        self.unit = unit
        self.command = command
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x")
        
        ctk.CTkLabel(
            header, text=label,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_dim"]
        ).pack(side="left")
        
        self.value_label = ctk.CTkLabel(
            header,
            text=f"{default or from_}{unit}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text"]
        )
        self.value_label.pack(side="right")
        
        # Slider
        self.slider = ctk.CTkSlider(
            self,
            from_=from_,
            to=to,
            command=self._on_change
        )
        self.slider.set(default or from_)
        self.slider.pack(fill="x", pady=(5, 0))
    
    def _on_change(self, value):
        self.value_label.configure(text=f"{int(value)}{self.unit}")
        if self.command:
            self.command(value)
    
    def get(self) -> float:
        return self.slider.get()
    
    def set(self, value: float):
        self.slider.set(value)
        self.value_label.configure(text=f"{int(value)}{self.unit}")


class SidebarButton(ctk.CTkButton):
    """Sidebar navigasyon butonu"""
    
    def __init__(self, parent, text: str, icon: str, command: Callable, **kwargs):
        super().__init__(
            parent,
            text=f"  {icon}  {text}",
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            anchor="w",
            height=45,
            corner_radius=8,
            command=command,
            **kwargs
        )
        self.is_active = False
    
    def set_active(self, active: bool):
        self.is_active = active
        if active:
            self.configure(fg_color=COLORS["accent"])
        else:
            self.configure(fg_color="transparent")


# ============================================================
# ANA PENCERE
# ============================================================

class MainWindow(ctk.CTk):
    """LinuxShorts Pro v2.0 - Modern Ana Pencere"""
    
    def __init__(self):
        super().__init__()
        
        logger.info("LinuxShorts Pro v2.0 başlatılıyor...")
        
        # Tema ayarları
        ctk.set_appearance_mode(APPEARANCE_MODE)
        ctk.set_default_color_theme(THEME)
        
        # Pencere ayarları
        self.title(f"{APP_NAME} Pro v2.0")
        self.geometry("1400x950")
        self.minsize(1200, 750)
        self.configure(fg_color=COLORS["bg_dark"])
        
        # Durum değişkenleri
        self.current_video_path: Optional[Path] = None
        self.current_video_info = None
        self.current_page = "home"
        self.sidebar_buttons = {}
        
        # Modülleri yükle
        self._load_modules()
        
        # GUI oluştur
        self._create_layout()
        self._create_sidebar()
        self._create_pages()
        
        # İlk sayfa
        self._show_page("home")
        
        logger.info("LinuxShorts Pro v2.0 hazır!")
    
    def _load_modules(self):
        """Core modülleri yükle"""
        try:
            from core.ffmpeg_wrapper import FFmpegWrapper, VideoInfo
            self.ffmpeg = FFmpegWrapper()
            self.VideoInfo = VideoInfo
            logger.info("FFmpeg modülü yüklendi")
        except Exception as e:
            logger.error(f"FFmpeg modülü yüklenemedi: {e}")
            self.ffmpeg = None
        
        try:
            from core.subtitle_generator import SubtitleGenerator
            self.subtitle_gen = SubtitleGenerator()
            logger.info("Altyazı modülü yüklendi")
        except Exception as e:
            logger.warning(f"Altyazı modülü yüklenemedi: {e}")
            self.subtitle_gen = None
        
        try:
            from core.video_analyzer import VideoAnalyzer
            self.video_analyzer = VideoAnalyzer()
            logger.info("Video analiz modülü yüklendi")
        except Exception as e:
            logger.warning(f"Video analiz modülü yüklenemedi: {e}")
            self.video_analyzer = None
        
        try:
            from core.hashtag_generator import HashtagGenerator
            self.hashtag_gen = HashtagGenerator()
            logger.info("Hashtag modülü yüklendi")
        except Exception as e:
            logger.warning(f"Hashtag modülü yüklenemedi: {e}")
            self.hashtag_gen = None
        
        try:
            from core.smart_analyzer import SmartVideoAnalyzer
            self.smart_analyzer = SmartVideoAnalyzer()
            logger.info("Akıllı analiz modülü yüklendi")
        except Exception as e:
            logger.warning(f"Akıllı analiz modülü yüklenemedi: {e}")
            self.smart_analyzer = None
        
        try:
            from core.thumbnail_generator import ThumbnailGenerator
            self.thumbnail_gen = ThumbnailGenerator()
            logger.info("Thumbnail modülü yüklendi")
        except Exception as e:
            logger.warning(f"Thumbnail modülü yüklenemedi: {e}")
            self.thumbnail_gen = None
        
        try:
            from core.seo_generator import SEOGenerator
            self.seo_gen = SEOGenerator()
            logger.info("SEO modülü yüklendi")
        except Exception as e:
            logger.warning(f"SEO modülü yüklenemedi: {e}")
            self.seo_gen = None
    
    def _create_layout(self):
        """Ana layout oluştur"""
        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=1)  # Content
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar container
        self.sidebar = ctk.CTkFrame(self, width=220, fg_color=COLORS["bg_card"], corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Content container
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)
    
    def _create_sidebar(self):
        """Sidebar navigasyonu oluştur"""
        # Logo/Başlık
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=15, pady=20)
        
        ctk.CTkLabel(
            logo_frame,
            text="🎬 LinuxShorts",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["accent"]
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            logo_frame,
            text="Pro v2.0",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_dim"]
        ).pack(anchor="w")
        
        # Ayırıcı
        ctk.CTkFrame(self.sidebar, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=15, pady=10)
        
        # Navigasyon butonları
        nav_items = [
            ("home", "🏠", "Ana Sayfa"),
            ("editor", "🎨", "Video Düzenle"),
            ("analysis", "🧠", "Akıllı Analiz"),
            ("subtitle", "📝", "Altyazı"),
            ("thumbnail", "🖼️", "Thumbnail"),
            ("seo", "📊", "SEO & Hashtag"),
            ("export", "🚀", "Export"),
        ]
        
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=10, pady=5)
        
        for page_id, icon, label in nav_items:
            btn = SidebarButton(
                nav_frame,
                text=label,
                icon=icon,
                command=lambda p=page_id: self._show_page(p)
            )
            btn.pack(fill="x", pady=2)
            self.sidebar_buttons[page_id] = btn
        
        # Alt kısım - Video bilgisi
        self.video_info_frame = ctk.CTkFrame(self.sidebar, fg_color=COLORS["bg_dark"], corner_radius=10)
        self.video_info_frame.pack(fill="x", padx=10, pady=10, side="bottom")
        
        self.video_info_label = ctk.CTkLabel(
            self.video_info_frame,
            text="📹 Video seçilmedi",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_dim"],
            wraplength=180
        )
        self.video_info_label.pack(pady=15, padx=10)
    
    def _create_pages(self):
        """Tüm sayfaları oluştur"""
        self.pages = {}
        
        # Her sayfa için frame
        for page_id in ["home", "editor", "analysis", "subtitle", "thumbnail", "seo", "export"]:
            frame = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
            frame.grid(row=0, column=0, sticky="nsew")
            self.pages[page_id] = frame
        
        # Sayfa içeriklerini oluştur
        self._create_home_page()
        self._create_editor_page()
        self._create_analysis_page()
        self._create_subtitle_page()
        self._create_thumbnail_page()
        self._create_seo_page()
        self._create_export_page()
    
    def _show_page(self, page_id: str):
        """Sayfa göster"""
        self.current_page = page_id
        
        # Tüm sayfaları gizle
        for pid, frame in self.pages.items():
            frame.grid_remove()
        
        # Seçili sayfayı göster
        self.pages[page_id].grid()
        
        # Sidebar butonlarını güncelle
        for pid, btn in self.sidebar_buttons.items():
            btn.set_active(pid == page_id)
    
    # ============================================================
    # ANA SAYFA
    # ============================================================
    
    def _create_home_page(self):
        """Ana sayfa - Hızlı başlangıç"""
        page = self.pages["home"]
        
        # Karşılama
        welcome = ModernCard(page, title="Hoş Geldiniz", icon="👋")
        welcome.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            welcome.get_content(),
            text="LinuxShorts Pro ile yatay videolarınızı profesyonel\nYouTube Shorts'a dönüştürün.",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_dim"],
            justify="left"
        ).pack(anchor="w")
        
        # Video Seçimi
        video_card = ModernCard(page, title="Video Seç", icon="🎬")
        video_card.pack(fill="x", pady=(0, 15))
        
        ModernButton(
            video_card.get_content(),
            text="Video Dosyası Seç",
            icon="📂",
            variant="primary",
            height=50,
            command=self._select_video
        ).pack(fill="x")
        
        ctk.CTkLabel(
            video_card.get_content(),
            text="Desteklenen formatlar: MP4, AVI, MKV, MOV, FLV, WMV",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_dim"]
        ).pack(pady=(10, 0))
        
        # Hızlı işlemler
        quick_card = ModernCard(page, title="Hızlı İşlemler", icon="⚡")
        quick_card.pack(fill="x", pady=(0, 15))
        
        quick_frame = ctk.CTkFrame(quick_card.get_content(), fg_color="transparent")
        quick_frame.pack(fill="x")
        quick_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        quick_actions = [
            ("🎨", "Düzenle", lambda: self._show_page("editor")),
            ("📝", "Altyazı", lambda: self._show_page("subtitle")),
            ("🚀", "Export", lambda: self._show_page("export")),
        ]
        
        for i, (icon, text, cmd) in enumerate(quick_actions):
            btn = ModernButton(
                quick_frame,
                text=text,
                icon=icon,
                variant="secondary",
                height=60,
                command=cmd
            )
            btn.grid(row=0, column=i, padx=5, sticky="ew")
        
        # Özellikler
        features_card = ModernCard(page, title="Özellikler", icon="✨")
        features_card.pack(fill="x")
        
        features = [
            ("🧠", "Akıllı Analiz", "Sessizlik algılama, hook tespiti, sahne değişiklikleri"),
            ("📝", "AI Altyazı", "Whisper ile otomatik altyazı oluşturma"),
            ("🖼️", "Thumbnail", "Otomatik en iyi frame seçimi ve düzenleme"),
            ("📊", "SEO", "Başlık, açıklama ve hashtag önerileri"),
            ("🎨", "Video Düzenle", "Zoom, pozisyon, arka plan efektleri"),
        ]
        
        for icon, title, desc in features:
            row = ctk.CTkFrame(features_card.get_content(), fg_color="transparent")
            row.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                row, text=icon,
                font=ctk.CTkFont(size=20)
            ).pack(side="left", padx=(0, 10))
            
            text_frame = ctk.CTkFrame(row, fg_color="transparent")
            text_frame.pack(side="left", fill="x", expand=True)
            
            ctk.CTkLabel(
                text_frame, text=title,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS["text"],
                anchor="w"
            ).pack(fill="x")
            
            ctk.CTkLabel(
                text_frame, text=desc,
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_dim"],
                anchor="w"
            ).pack(fill="x")
    
    # ============================================================
    # VIDEO DÜZENLEME SAYFASI
    # ============================================================
    
    def _create_editor_page(self):
        """Video düzenleme sayfası"""
        page = self.pages["editor"]
        
        # 2 sütunlu layout
        page.grid_columnconfigure(0, weight=2)
        page.grid_columnconfigure(1, weight=1)
        
        # Drag state
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.current_pos_x = 0
        self.current_pos_y = 0
        self.current_scale = 100
        
        # Sol - Önizleme
        preview_card = ModernCard(page, title="Önizleme (Fare: Sürükle | Scroll: Zoom)", icon="👁️")
        preview_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        
        # Önizleme Canvas (320x568 - 9:16 shorts formatı)
        self.canvas_width = 320
        self.canvas_height = 568
        
        from tkinter import Canvas
        self.preview_canvas = Canvas(
            preview_card.get_content(),
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#000000",
            highlightthickness=2,
            highlightbackground=COLORS["border"]
        )
        self.preview_canvas.pack(pady=10)
        
        # Canvas'a "Video Yükle" yazısı
        self.preview_canvas.create_text(
            self.canvas_width // 2, self.canvas_height // 2,
            text="📹 Video yükleyin\n\n🖱️ Fare ile sürükleyin\n🔄 Scroll ile zoom yapın",
            fill=COLORS["text_dim"],
            font=("Arial", 12),
            justify="center",
            tags="placeholder"
        )
        
        # Fare event'leri
        self.preview_canvas.bind("<ButtonPress-1>", self._on_canvas_drag_start)
        self.preview_canvas.bind("<B1-Motion>", self._on_canvas_drag_motion)
        self.preview_canvas.bind("<ButtonRelease-1>", self._on_canvas_drag_end)
        self.preview_canvas.bind("<MouseWheel>", self._on_canvas_scroll)  # Windows/MacOS
        self.preview_canvas.bind("<Button-4>", lambda e: self._on_canvas_scroll_linux(1))  # Linux scroll up
        self.preview_canvas.bind("<Button-5>", lambda e: self._on_canvas_scroll_linux(-1))  # Linux scroll down
        
        # Zaman kontrolü
        time_frame = ctk.CTkFrame(preview_card.get_content(), fg_color="transparent")
        time_frame.pack(fill="x", pady=10)
        
        self.time_slider = ctk.CTkSlider(
            time_frame, 
            from_=0, 
            to=100,
            command=self._on_time_slider_change
        )
        self.time_slider.pack(fill="x")
        
        self.time_label = ctk.CTkLabel(
            time_frame,
            text="00:00 / 00:00",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_dim"]
        )
        self.time_label.pack()
        
        # Sağ - Kontroller
        controls_frame = ctk.CTkFrame(page, fg_color="transparent")
        controls_frame.grid(row=0, column=1, sticky="nsew")
        
        # Transform
        transform_card = ModernCard(controls_frame, title="Transform", icon="📐")
        transform_card.pack(fill="x", pady=(0, 10))
        
        self.scale_slider = ModernSlider(
            transform_card.get_content(),
            label="Ölçek (Zoom)",
            from_=30, to=300, default=100, unit="%",
            command=self._on_scale_change
        )
        self.scale_slider.pack(fill="x", pady=5)
        
        self.pos_x_slider = ModernSlider(
            transform_card.get_content(),
            label="X Pozisyon",
            from_=-500, to=500, default=0, unit="px",
            command=self._on_position_change
        )
        self.pos_x_slider.pack(fill="x", pady=5)
        
        self.pos_y_slider = ModernSlider(
            transform_card.get_content(),
            label="Y Pozisyon",
            from_=-500, to=500, default=0, unit="px",
            command=self._on_position_change
        )
        self.pos_y_slider.pack(fill="x", pady=5)
        
        # Hızlı butonlar
        quick_btns = ctk.CTkFrame(transform_card.get_content(), fg_color="transparent")
        quick_btns.pack(fill="x", pady=(10, 0))
        
        ModernButton(quick_btns, text="Ortala", variant="ghost", width=70, command=self._center_video).pack(side="left", padx=2)
        ModernButton(quick_btns, text="Sığdır", variant="ghost", width=70, command=self._fit_video).pack(side="left", padx=2)
        ModernButton(quick_btns, text="Doldur", variant="ghost", width=70, command=self._fill_video).pack(side="left", padx=2)
        ModernButton(quick_btns, text="Sıfırla", variant="ghost", width=70, command=self._reset_transform).pack(side="left", padx=2)
        
        # Zaman Aralığı
        time_card = ModernCard(controls_frame, title="Zaman Aralığı", icon="⏱️")
        time_card.pack(fill="x", pady=(0, 10))
        
        time_grid = ctk.CTkFrame(time_card.get_content(), fg_color="transparent")
        time_grid.pack(fill="x")
        time_grid.grid_columnconfigure((0, 1), weight=1)
        
        # Başlangıç
        start_frame = ctk.CTkFrame(time_grid, fg_color="transparent")
        start_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        ctk.CTkLabel(start_frame, text="Başlangıç:", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.start_time_entry = ctk.CTkEntry(start_frame, placeholder_text="00:00:00")
        self.start_time_entry.pack(fill="x", pady=(5, 0))
        # Entry değiştiğinde slider'ı güncelle
        self.start_time_entry.bind("<Return>", self._on_start_time_change)
        self.start_time_entry.bind("<FocusOut>", self._on_start_time_change)
        
        # Süre
        dur_frame = ctk.CTkFrame(time_grid, fg_color="transparent")
        dur_frame.grid(row=0, column=1, sticky="ew")
        
        ctk.CTkLabel(dur_frame, text="Süre (saniye):", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.duration_entry = ctk.CTkEntry(dur_frame, placeholder_text="60")
        self.duration_entry.pack(fill="x", pady=(5, 0))
        self.duration_entry.insert(0, "60")
        
        # Arka Plan
        bg_card = ModernCard(controls_frame, title="Arka Plan", icon="🎨")
        bg_card.pack(fill="x", pady=(0, 10))
        
        self.bg_mode = ctk.StringVar(value="blur")
        
        bg_options = ctk.CTkFrame(bg_card.get_content(), fg_color="transparent")
        bg_options.pack(fill="x")
        
        for value, text in [("black", "⬛ Siyah"), ("blur", "🌫️ Blur"), ("color", "🎨 Renk")]:
            rb = ctk.CTkRadioButton(
                bg_options,
                text=text,
                variable=self.bg_mode,
                value=value,
                font=ctk.CTkFont(size=12),
                command=self._on_bg_mode_change
            )
            rb.pack(side="left", padx=5)
        
        # Renk seçici (color mode için)
        self.bg_color = "#333333"
        color_frame = ctk.CTkFrame(bg_card.get_content(), fg_color="transparent")
        color_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkLabel(color_frame, text="Arka Plan Rengi:", font=ctk.CTkFont(size=11)).pack(side="left")
        
        self.bg_color_btn = ctk.CTkButton(
            color_frame,
            text="",
            width=40,
            height=25,
            fg_color=self.bg_color,
            hover_color=self.bg_color,
            command=self._pick_bg_color
        )
        self.bg_color_btn.pack(side="left", padx=10)
        
        self.blur_slider = ModernSlider(
            bg_card.get_content(),
            label="Blur Gücü",
            from_=5, to=50, default=25,
            command=self._on_blur_change
        )
        self.blur_slider.pack(fill="x", pady=(10, 0))
        
        # Kalite Ayarları
        quality_card = ModernCard(controls_frame, title="Kalite", icon="⚙️")
        quality_card.pack(fill="x", pady=(0, 10))
        
        self.crf_slider = ModernSlider(
            quality_card.get_content(),
            label="Video Kalitesi (CRF)",
            from_=18, to=28, default=23
        )
        self.crf_slider.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(
            quality_card.get_content(),
            text="Düşük CRF = Yüksek kalite, büyük dosya",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_dim"]
        ).pack(anchor="w")
        
        preset_frame = ctk.CTkFrame(quality_card.get_content(), fg_color="transparent")
        preset_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkLabel(preset_frame, text="Hız:", font=ctk.CTkFont(size=12)).pack(side="left")
        
        self.preset_var = ctk.StringVar(value="medium")
        self.preset_menu = ctk.CTkOptionMenu(
            preset_frame,
            variable=self.preset_var,
            values=["ultrafast", "fast", "medium", "slow"],
            width=100
        )
        self.preset_menu.pack(side="right")
        
        # Durum bilgisi
        status_card = ModernCard(controls_frame, title="Durum", icon="ℹ️")
        status_card.pack(fill="x")
        
        self.editor_status = ctk.CTkLabel(
            status_card.get_content(),
            text="Video yükleyin",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_dim"]
        )
        self.editor_status.pack(anchor="w")
    
    # ============================================================
    # AKILLI ANALİZ SAYFASI
    # ============================================================
    
    def _create_analysis_page(self):
        """Akıllı analiz sayfası"""
        page = self.pages["analysis"]
        
        # Başlık
        header_card = ModernCard(page, title="Akıllı Video Analizi", icon="🧠")
        header_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            header_card.get_content(),
            text="Sessizlik algılama, hook tespiti, sahne değişiklikleri ve en iyi kesit önerileri",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_dim"]
        ).pack(anchor="w")
        
        ModernButton(
            header_card.get_content(),
            text="Analizi Başlat",
            icon="🔍",
            variant="primary",
            height=45,
            command=self._start_analysis
        ).pack(fill="x", pady=(15, 0))
        
        # Progress
        self.analysis_progress = ctk.CTkProgressBar(header_card.get_content())
        self.analysis_progress.pack(fill="x", pady=(10, 0))
        self.analysis_progress.set(0)
        
        self.analysis_status = ctk.CTkLabel(
            header_card.get_content(),
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_dim"]
        )
        self.analysis_status.pack(pady=(5, 0))
        
        # Sonuçlar
        self.analysis_results_frame = ModernCard(page, title="Sonuçlar", icon="📊")
        self.analysis_results_frame.pack(fill="both", expand=True)
        
        self.analysis_results = ctk.CTkLabel(
            self.analysis_results_frame.get_content(),
            text="Analiz sonuçları burada görünecek...",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_dim"],
            justify="left"
        )
        self.analysis_results.pack(pady=10, anchor="w")
        
        # Kesit kullanma butonu
        self.use_segment_btn = ModernButton(
            self.analysis_results_frame.get_content(),
            text="⭐ En İyi Kesiti Kullan",
            icon="✓",
            variant="success",
            command=self._use_best_segment
        )
        # Başlangıçta gizli
        
        # Analiz sonucu değişkeni
        self.last_analysis_result = None
    
    # ============================================================
    # ALTYAZI SAYFASI
    # ============================================================
    
    def _create_subtitle_page(self):
        """Altyazı sayfası"""
        page = self.pages["subtitle"]
        
        # 2 sütunlu layout
        page.grid_columnconfigure(0, weight=1)
        page.grid_columnconfigure(1, weight=1)
        page.grid_rowconfigure(0, weight=1)
        
        # ============================================================
        # SOL TARAF - Önizleme, Oluşturma, Stil
        # ============================================================
        left_frame = ctk.CTkFrame(page, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Önizleme
        preview_card = ModernCard(left_frame, title="Altyazı Önizleme", icon="👁️")
        preview_card.pack(fill="x", pady=(0, 10))
        
        # Önizleme canvas
        from tkinter import Canvas
        self.subtitle_preview_canvas = Canvas(
            preview_card.get_content(),
            width=320,
            height=180,
            bg="#000000",
            highlightthickness=1,
            highlightbackground=COLORS["border"]
        )
        self.subtitle_preview_canvas.pack(pady=10)
        
        # Örnek altyazı metni
        self.subtitle_preview_canvas.create_text(
            160, 160,
            text="Örnek Altyazı Metni",
            fill="#FFFFFF",
            font=("Arial", 16, "bold"),
            tags="subtitle_text"
        )
        
        # Altyazı oluşturma
        create_card = ModernCard(left_frame, title="Altyazı Oluştur", icon="📝")
        create_card.pack(fill="x", pady=(0, 10))
        
        # Whisper model seçimi
        model_frame = ctk.CTkFrame(create_card.get_content(), fg_color="transparent")
        model_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(model_frame, text="Model:", font=ctk.CTkFont(size=12)).pack(side="left")
        
        self.whisper_model = ctk.CTkOptionMenu(
            model_frame,
            values=["tiny", "base", "small", "medium", "large"],
            width=120
        )
        self.whisper_model.set("small")
        self.whisper_model.pack(side="left", padx=10)
        
        # Zaman aralığı seçeneği
        self.subtitle_use_timerange = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            create_card.get_content(),
            text="Sadece seçilen zaman aralığı için oluştur",
            variable=self.subtitle_use_timerange,
            font=ctk.CTkFont(size=11)
        ).pack(anchor="w", pady=(0, 10))
        
        # Zaman bilgisi
        self.subtitle_time_info = ctk.CTkLabel(
            create_card.get_content(),
            text="⏱️ Zaman aralığı: Video Düzenleme'den alınır",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_dim"]
        )
        self.subtitle_time_info.pack(anchor="w", pady=(0, 10))
        
        ModernButton(
            create_card.get_content(),
            text="Altyazı Oluştur",
            icon="✨",
            variant="primary",
            command=self._generate_subtitles
        ).pack(fill="x")
        
        # Progress
        self.subtitle_progress = ctk.CTkProgressBar(create_card.get_content())
        self.subtitle_progress.pack(fill="x", pady=(10, 0))
        self.subtitle_progress.set(0)
        
        self.subtitle_status = ctk.CTkLabel(
            create_card.get_content(),
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_dim"]
        )
        self.subtitle_status.pack(pady=(5, 0))
        
        # Stil ayarları
        style_card = ModernCard(left_frame, title="Altyazı Stili", icon="🎨")
        style_card.pack(fill="x")
        
        # Pozisyon
        pos_frame = ctk.CTkFrame(style_card.get_content(), fg_color="transparent")
        pos_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(pos_frame, text="Pozisyon:", font=ctk.CTkFont(size=12)).pack(side="left")
        
        self.subtitle_position = ctk.StringVar(value="bottom")
        for pos, text in [("top", "Üst"), ("center", "Orta"), ("bottom", "Alt")]:
            ctk.CTkRadioButton(
                pos_frame,
                text=text,
                variable=self.subtitle_position,
                value=pos,
                font=ctk.CTkFont(size=11),
                command=self._update_subtitle_preview
            ).pack(side="left", padx=5)
        
        # Font boyutu
        self.subtitle_fontsize = ModernSlider(
            style_card.get_content(),
            label="Font Boyutu",
            from_=8, to=48, default=16, unit="px",
            command=self._on_subtitle_style_change
        )
        self.subtitle_fontsize.pack(fill="x", pady=(0, 10))
        
        # Renk seçimi
        color_frame = ctk.CTkFrame(style_card.get_content(), fg_color="transparent")
        color_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(color_frame, text="Renk:", font=ctk.CTkFont(size=12)).pack(side="left")
        
        self.subtitle_color = "#FFFFFF"
        self.subtitle_color_btn = ctk.CTkButton(
            color_frame,
            text="",
            width=40,
            height=25,
            fg_color=self.subtitle_color,
            hover_color=self.subtitle_color,
            command=self._pick_subtitle_color
        )
        self.subtitle_color_btn.pack(side="left", padx=10)
        
        # Arka plan
        self.subtitle_bg_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            style_card.get_content(),
            text="Yarı saydam arka plan",
            variable=self.subtitle_bg_var,
            command=self._update_subtitle_preview
        ).pack(anchor="w")
        
        # ============================================================
        # SAĞ TARAF - Altyazı Düzenleme (Tam boy)
        # ============================================================
        right_frame = ctk.CTkFrame(page, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        # Altyazı düzenleme
        edit_card = ModernCard(right_frame, title="Altyazı Düzenle (SRT Formatı)", icon="✏️")
        edit_card.pack(fill="both", expand=True)
        
        self.subtitle_text = ctk.CTkTextbox(
            edit_card.get_content(),
            font=ctk.CTkFont(family="Courier", size=12)
        )
        self.subtitle_text.pack(fill="both", expand=True, pady=(0, 10))
        
        # Alt butonlar
        btn_frame = ctk.CTkFrame(edit_card.get_content(), fg_color="transparent")
        btn_frame.pack(fill="x")
        
        ModernButton(
            btn_frame,
            text="SRT Kaydet",
            icon="💾",
            variant="secondary",
            width=120,
            command=self._save_subtitle_srt
        ).pack(side="left", padx=(0, 5))
        
        ModernButton(
            btn_frame,
            text="Kopyala",
            icon="📋",
            variant="ghost",
            width=100,
            command=self._copy_subtitles
        ).pack(side="left")
    
    # ============================================================
    # THUMBNAIL SAYFASI
    # ============================================================
    
    def _create_thumbnail_page(self):
        """Thumbnail sayfası"""
        page = self.pages["thumbnail"]
        
        # 2 sütun
        page.grid_columnconfigure(0, weight=1)
        page.grid_columnconfigure(1, weight=1)
        
        # Sol - Önizleme
        preview_card = ModernCard(page, title="Önizleme", icon="🖼️")
        preview_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Önizleme canvas
        from tkinter import Canvas
        self.thumb_canvas = Canvas(
            preview_card.get_content(),
            width=320,
            height=180,
            bg="#000000",
            highlightthickness=1,
            highlightbackground=COLORS["border"]
        )
        self.thumb_canvas.pack(pady=10)
        
        # Zaman seçici
        self.thumb_time = ModernSlider(
            preview_card.get_content(),
            label="Zaman",
            from_=0, to=100, default=0, unit="s",
            command=self._on_thumb_time_change
        )
        self.thumb_time.pack(fill="x", pady=10)
        
        ModernButton(
            preview_card.get_content(),
            text="En İyi Frame'leri Bul",
            icon="🔍",
            variant="secondary",
            command=self._find_best_frames
        ).pack(fill="x", pady=(0, 10))
        
        # En iyi frame'ler listesi
        self.best_frames_frame = ctk.CTkFrame(preview_card.get_content(), fg_color="transparent")
        self.best_frames_frame.pack(fill="x")
        
        self.best_frames_label = ctk.CTkLabel(
            self.best_frames_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_dim"],
            justify="left"
        )
        self.best_frames_label.pack(anchor="w")
        
        # Sağ - Ayarlar
        settings_card = ModernCard(page, title="Ayarlar", icon="⚙️")
        settings_card.grid(row=0, column=1, sticky="nsew")
        
        # Başlık
        ctk.CTkLabel(
            settings_card.get_content(),
            text="Başlık Metni:",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w")
        
        self.thumb_title = ctk.CTkEntry(
            settings_card.get_content(),
            placeholder_text="Thumbnail başlığı..."
        )
        self.thumb_title.pack(fill="x", pady=(5, 15))
        
        # Efektler
        self.thumb_vignette = ctk.CTkCheckBox(
            settings_card.get_content(),
            text="Vignette Efekti",
            command=self._update_thumbnail_effects
        )
        self.thumb_vignette.pack(anchor="w")
        self.thumb_vignette.select()
        
        self.thumb_brightness = ModernSlider(
            settings_card.get_content(),
            label="Parlaklık",
            from_=50, to=150, default=110, unit="%",
            command=self._on_thumb_effect_change
        )
        self.thumb_brightness.pack(fill="x", pady=10)
        
        self.thumb_contrast = ModernSlider(
            settings_card.get_content(),
            label="Kontrast",
            from_=50, to=150, default=120, unit="%",
            command=self._on_thumb_effect_change
        )
        self.thumb_contrast.pack(fill="x", pady=10)
        
        self.thumb_saturation = ModernSlider(
            settings_card.get_content(),
            label="Doygunluk",
            from_=50, to=150, default=100, unit="%",
            command=self._on_thumb_effect_change
        )
        self.thumb_saturation.pack(fill="x", pady=10)
        
        # Kaydet
        ModernButton(
            settings_card.get_content(),
            text="Thumbnail Kaydet",
            icon="💾",
            variant="success",
            command=self._save_thumbnail
        ).pack(fill="x", pady=(20, 0))
    
    # ============================================================
    # SEO SAYFASI
    # ============================================================
    
    def _create_seo_page(self):
        """SEO ve hashtag sayfası"""
        page = self.pages["seo"]
        
        # Konu girişi
        topic_card = ModernCard(page, title="Video Konusu", icon="📌")
        topic_card.pack(fill="x", pady=(0, 15))
        
        self.seo_topic = ctk.CTkEntry(
            topic_card.get_content(),
            placeholder_text="Örn: Linux Terminal, Python Eğitimi...",
            height=40
        )
        self.seo_topic.pack(fill="x", pady=(0, 10))
        
        ModernButton(
            topic_card.get_content(),
            text="Öneriler Oluştur",
            icon="✨",
            variant="primary",
            command=self._generate_seo
        ).pack(fill="x")
        
        # Öneriler
        self.seo_results_card = ModernCard(page, title="Öneriler", icon="💡")
        self.seo_results_card.pack(fill="both", expand=True, pady=(0, 15))
        
        # Başlık önerisi
        ctk.CTkLabel(
            self.seo_results_card.get_content(),
            text="📌 Önerilen Başlık:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")
        
        self.seo_title = ctk.CTkEntry(
            self.seo_results_card.get_content(),
            height=40
        )
        self.seo_title.pack(fill="x", pady=(5, 15))
        
        # Hashtag'ler
        ctk.CTkLabel(
            self.seo_results_card.get_content(),
            text="🏷️ Önerilen Hashtag'ler:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")
        
        self.seo_hashtags = ctk.CTkTextbox(
            self.seo_results_card.get_content(),
            height=100
        )
        self.seo_hashtags.pack(fill="x", pady=(5, 15))
        
        # Açıklama
        ctk.CTkLabel(
            self.seo_results_card.get_content(),
            text="📝 Önerilen Açıklama:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")
        
        self.seo_description = ctk.CTkTextbox(
            self.seo_results_card.get_content(),
            height=150
        )
        self.seo_description.pack(fill="both", expand=True, pady=(5, 0))
        
        # Kopyala butonu
        ModernButton(
            self.seo_results_card.get_content(),
            text="Tümünü Kopyala",
            icon="📋",
            variant="secondary",
            command=self._copy_seo
        ).pack(fill="x", pady=(10, 0))
    
    # ============================================================
    # EXPORT SAYFASI
    # ============================================================
    
    def _create_export_page(self):
        """Export sayfası"""
        page = self.pages["export"]
        
        # Özet
        summary_card = ModernCard(page, title="Export Özeti", icon="📋")
        summary_card.pack(fill="x", pady=(0, 15))
        
        self.export_summary = ctk.CTkLabel(
            summary_card.get_content(),
            text="Video seçilmedi.\nExport için önce bir video yükleyin.",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_dim"],
            justify="left"
        )
        self.export_summary.pack(anchor="w")
        
        # Export Seçenekleri
        options_card = ModernCard(page, title="Export Seçenekleri", icon="⚙️")
        options_card.pack(fill="x", pady=(0, 15))
        
        # Altyazı gömme seçeneği
        self.burn_subtitles = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            options_card.get_content(),
            text="Altyazıyı videoya göm (burn-in)",
            variable=self.burn_subtitles,
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", pady=(0, 10))
        
        ctk.CTkLabel(
            options_card.get_content(),
            text="💡 Altyazı sayfasında oluşturduğunuz altyazılar videoya gömülür.",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_dim"]
        ).pack(anchor="w", pady=(0, 15))
        
        # Çıktı dizini
        output_frame = ctk.CTkFrame(options_card.get_content(), fg_color="transparent")
        output_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(output_frame, text="Kayıt Yeri:", font=ctk.CTkFont(size=12)).pack(side="left")
        
        self.output_dir_var = ctk.StringVar(value=str(OUTPUT_DIR))
        self.output_dir_entry = ctk.CTkEntry(
            output_frame,
            textvariable=self.output_dir_var,
            width=250
        )
        self.output_dir_entry.pack(side="left", padx=10, fill="x", expand=True)
        
        ModernButton(
            output_frame,
            text="📁",
            variant="ghost",
            width=40,
            command=self._select_output_dir
        ).pack(side="right")
        
        # Kullanılacak ayarlar özeti
        ctk.CTkLabel(
            options_card.get_content(),
            text="📌 Video Düzenleme'deki ayarlar: Zaman • Transform • Arka plan • Kalite",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_dim"]
        ).pack(anchor="w")
        
        ModernButton(
            options_card.get_content(),
            text="Video Düzenleme'ye Git",
            icon="🎬",
            variant="ghost",
            command=lambda: self._show_page("editor")
        ).pack(fill="x", pady=(10, 0))
        
        # Export butonu
        export_card = ModernCard(page, title="", icon="")
        export_card.pack(fill="x")
        
        ModernButton(
            export_card.get_content(),
            text="SHORT VIDEO OLUŞTUR",
            icon="🚀",
            variant="success",
            height=60,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._export_video
        ).pack(fill="x")
        
        # Progress
        self.export_progress = ctk.CTkProgressBar(export_card.get_content())
        self.export_progress.pack(fill="x", pady=(15, 0))
        self.export_progress.set(0)
        
        self.export_status = ctk.CTkLabel(
            export_card.get_content(),
            text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_dim"]
        )
        self.export_status.pack(pady=(10, 0))
    
    # ============================================================
    # FONKSİYONLAR
    # ============================================================
    
    def _select_video(self):
        """Video dosyası seç"""
        file_path = filedialog.askopenfilename(
            title="Video Seç",
            filetypes=SUPPORTED_VIDEO_FORMATS
        )
        
        if not file_path:
            return
        
        self.current_video_path = Path(file_path)
        
        try:
            if self.ffmpeg:
                self.current_video_info = self.ffmpeg.get_video_info(self.current_video_path)
                
                info_text = (
                    f"📹 {self.current_video_path.name}\n"
                    f"📐 {self.current_video_info.width}x{self.current_video_info.height}\n"
                    f"⏱️ {self.current_video_info.duration:.1f}s"
                )
                self.video_info_label.configure(text=info_text, text_color=COLORS["text"])
                
                # Export özeti güncelle
                self.export_summary.configure(
                    text=f"📹 {self.current_video_path.name}\n"
                         f"📐 {self.current_video_info.width}x{self.current_video_info.height}\n"
                         f"⏱️ {self.current_video_info.duration:.1f} saniye\n"
                         f"🎞️ {self.current_video_info.fps:.1f} FPS"
                )
                
                # Slider'ları güncelle
                duration = self.current_video_info.duration
                self.time_slider.configure(to=duration)
                self.time_slider.set(0)
                self.thumb_time.slider.configure(to=duration)
                self.thumb_time.set(0)
                
                # Zaman label güncelle
                total_min = int(duration // 60)
                total_sec = int(duration % 60)
                self.time_label.configure(text=f"00:00 / {total_min:02d}:{total_sec:02d}")
                
                # Preview'ları güncelle
                self._update_editor_preview(0)
                self._update_thumbnail_preview(0)
                
                logger.info(f"Video seçildi: {self.current_video_path}")
                messagebox.showinfo("Başarılı", f"Video yüklendi:\n{self.current_video_path.name}")
                
        except Exception as e:
            logger.error(f"Video yükleme hatası: {e}")
            messagebox.showerror("Hata", f"Video yüklenemedi:\n{e}")
    
    def _get_video_frame(self, time_sec: float, width: int = 320, height: int = 568) -> Optional[ImageTk.PhotoImage]:
        """Videodan belirli zamandaki frame'i al"""
        if not CV2_AVAILABLE or not self.current_video_path:
            return None
        
        try:
            cap = cv2.VideoCapture(str(self.current_video_path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_num = int(time_sec * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return None
            
            # BGR -> RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Boyutlandır (aspect ratio koruyarak)
            h, w = frame.shape[:2]
            aspect = w / h
            target_aspect = width / height
            
            if aspect > target_aspect:
                # Video daha geniş, yüksekliğe göre ölçekle
                new_h = height
                new_w = int(height * aspect)
            else:
                # Video daha uzun, genişliğe göre ölçekle
                new_w = width
                new_h = int(width / aspect)
            
            frame = cv2.resize(frame, (new_w, new_h))
            
            # Ortala ve kırp
            start_x = (new_w - width) // 2
            start_y = (new_h - height) // 2
            frame = frame[start_y:start_y+height, start_x:start_x+width]
            
            # PIL Image'e çevir
            img = Image.fromarray(frame)
            return ImageTk.PhotoImage(img)
            
        except Exception as e:
            logger.error(f"Frame alma hatası: {e}")
            return None
    
    def _get_transformed_frame(self, time_sec: float) -> Optional[ImageTk.PhotoImage]:
        """Transform uygulanmış frame al"""
        if not CV2_AVAILABLE or not self.current_video_path:
            return None
        
        try:
            cap = cv2.VideoCapture(str(self.current_video_path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_num = int(time_sec * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return None
            
            # BGR -> RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Video orijinal boyutları
            orig_h, orig_w = frame.shape[:2]
            
            # FIT SCALE: Videoyu canvas'a sığdırmak için gereken scale
            # %100 zoom = video tam olarak canvas'a sığar
            fit_scale_w = self.canvas_width / orig_w
            fit_scale_h = self.canvas_height / orig_h
            fit_scale = min(fit_scale_w, fit_scale_h)
            
            # Kullanıcının zoom değerini uygula (%100 = fit)
            user_zoom = self.current_scale / 100.0
            final_scale = fit_scale * user_zoom
            
            # Yeni boyutlar
            new_w = int(orig_w * final_scale)
            new_h = int(orig_h * final_scale)
            
            if new_w > 0 and new_h > 0:
                frame = cv2.resize(frame, (new_w, new_h))
            
            # Canvas boyutunda boş arka plan oluştur
            bg_mode = self.bg_mode.get()
            
            if bg_mode == "black":
                canvas_frame = np.zeros((self.canvas_height, self.canvas_width, 3), dtype=np.uint8)
            elif bg_mode == "blur":
                # Orijinal frame'den blur arka plan (canvas boyutuna scale edilmiş)
                blur_strength = int(self.blur_slider.get())
                blur_strength = blur_strength if blur_strength % 2 == 1 else blur_strength + 1
                
                # Orijinal frame'i canvas boyutuna scale et (crop ile)
                orig_frame = cv2.cvtColor(cv2.resize(
                    cv2.imread(str(self.current_video_path)), 
                    (self.canvas_width, self.canvas_height)
                ) if False else frame, cv2.COLOR_RGB2BGR)
                
                # Blur için orijinal frame'i kullan
                cap2 = cv2.VideoCapture(str(self.current_video_path))
                cap2.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret2, blur_frame = cap2.read()
                cap2.release()
                
                if ret2:
                    blur_frame = cv2.cvtColor(blur_frame, cv2.COLOR_BGR2RGB)
                    # Blur arka planı canvas boyutuna scale et (aspect ratio'yu korumadan, fill)
                    blur_frame = cv2.resize(blur_frame, (self.canvas_width, self.canvas_height))
                    canvas_frame = cv2.GaussianBlur(blur_frame, (blur_strength, blur_strength), 0)
                else:
                    canvas_frame = np.zeros((self.canvas_height, self.canvas_width, 3), dtype=np.uint8)
                    
            elif bg_mode == "color":
                # Kullanıcının seçtiği renk
                hex_color = self.bg_color.lstrip('#')
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                canvas_frame = np.full((self.canvas_height, self.canvas_width, 3), [r, g, b], dtype=np.uint8)
            else:
                # Varsayılan siyah arka plan
                canvas_frame = np.zeros((self.canvas_height, self.canvas_width, 3), dtype=np.uint8)
            
            # Pozisyon hesapla
            pos_x = self.current_pos_x
            pos_y = self.current_pos_y
            
            # Video'yu canvas'a yerleştir
            # Canvas merkezine göre hesapla
            center_x = self.canvas_width // 2
            center_y = self.canvas_height // 2
            
            # Video'nun sol üst köşesi
            video_x = center_x - new_w // 2 + pos_x
            video_y = center_y - new_h // 2 + pos_y
            
            # Kırpma ve yerleştirme
            src_x1 = max(0, -video_x)
            src_y1 = max(0, -video_y)
            src_x2 = min(new_w, self.canvas_width - video_x)
            src_y2 = min(new_h, self.canvas_height - video_y)
            
            dst_x1 = max(0, video_x)
            dst_y1 = max(0, video_y)
            dst_x2 = min(self.canvas_width, video_x + new_w)
            dst_y2 = min(self.canvas_height, video_y + new_h)
            
            if src_x2 > src_x1 and src_y2 > src_y1 and dst_x2 > dst_x1 and dst_y2 > dst_y1:
                canvas_frame[dst_y1:dst_y2, dst_x1:dst_x2] = frame[src_y1:src_y2, src_x1:src_x2]
            
            # PIL Image'e çevir
            img = Image.fromarray(canvas_frame)
            return ImageTk.PhotoImage(img)
            
        except Exception as e:
            logger.error(f"Transformed frame hatası: {e}")
            return None
    
    def _update_editor_preview(self, time_sec: float = None):
        """Editor preview'ını güncelle (Canvas tabanlı)"""
        if time_sec is None:
            time_sec = self.time_slider.get()
        
        if not self.current_video_path:
            return
        
        # Placeholder'ı kaldır
        self.preview_canvas.delete("placeholder")
        
        # Transform uygulanmış frame al
        photo = self._get_transformed_frame(time_sec)
        
        if photo:
            # Referansı sakla (garbage collection engelleme)
            self._editor_photo = photo
            
            # Canvas'ı temizle ve yeni görüntüyü çiz
            self.preview_canvas.delete("preview")
            self.preview_canvas.create_image(
                self.canvas_width // 2, self.canvas_height // 2,
                image=photo,
                tags="preview"
            )
        
        # Durum güncelle
        self.editor_status.configure(
            text=f"Zoom: {self.current_scale}% | Pos: ({self.current_pos_x}, {self.current_pos_y})"
        )
        
        # Zaman label güncelle
        if self.current_video_info:
            cur_min = int(time_sec // 60)
            cur_sec = int(time_sec % 60)
            total = self.current_video_info.duration
            total_min = int(total // 60)
            total_sec = int(total % 60)
            self.time_label.configure(text=f"{cur_min:02d}:{cur_sec:02d} / {total_min:02d}:{total_sec:02d}")
    
    def _update_thumbnail_preview(self, time_sec: float = None):
        """Thumbnail preview'ını güncelle (eski, artık _update_thumbnail_with_effects kullanılıyor)"""
        self._update_thumbnail_with_effects()
    
    def _on_time_slider_change(self, value):
        """Zaman slider değiştiğinde"""
        # Önizlemeyi güncelle
        self._update_editor_preview(value)
        
        # Zaman label'ını güncelle
        if hasattr(self, 'current_video_info') and self.current_video_info:
            total = self.current_video_info.duration
            cur_min = int(value // 60)
            cur_sec = int(value % 60)
            total_min = int(total // 60)
            total_sec = int(total % 60)
            self.time_label.configure(text=f"{cur_min:02d}:{cur_sec:02d} / {total_min:02d}:{total_sec:02d}")
        
        # Başlangıç zamanını entry'ye yaz
        hours = int(value // 3600)
        mins = int((value % 3600) // 60)
        secs = int(value % 60)
        
        # Entry'yi güncelle (döngüyü önlemek için flag kullan)
        if not hasattr(self, '_updating_from_slider'):
            self._updating_from_slider = False
        
        if not self._updating_from_slider:
            self._updating_from_entry = True
            self.start_time_entry.delete(0, "end")
            self.start_time_entry.insert(0, f"{hours:02d}:{mins:02d}:{secs:02d}")
            self._updating_from_entry = False
    
    def _on_start_time_change(self, event=None):
        """Başlangıç zamanı entry'si değiştiğinde"""
        if hasattr(self, '_updating_from_entry') and self._updating_from_entry:
            return
        
        time_str = self.start_time_entry.get().strip()
        if not time_str:
            return
        
        try:
            # HH:MM:SS formatını parse et
            parts = time_str.split(":")
            if len(parts) == 3:
                hours = int(parts[0])
                mins = int(parts[1])
                secs = float(parts[2])
                total_secs = hours * 3600 + mins * 60 + secs
            elif len(parts) == 2:
                mins = int(parts[0])
                secs = float(parts[1])
                total_secs = mins * 60 + secs
            else:
                total_secs = float(time_str)
            
            # Slider'ı güncelle
            if hasattr(self, 'current_video_info') and self.current_video_info:
                max_time = self.current_video_info.duration
                total_secs = min(total_secs, max_time)
            
            self._updating_from_slider = True
            self.time_slider.set(total_secs)
            self._update_editor_preview(total_secs)
            self._updating_from_slider = False
            
        except (ValueError, IndexError):
            pass  # Geçersiz format, sessizce geç
    
    def _on_thumb_time_change(self, value):
        """Thumbnail zaman slider değiştiğinde"""
        self._update_thumbnail_with_effects()
    
    # ============================================================
    # CANVAS FARE EVENT HANDLER'LARI
    # ============================================================
    
    def _on_canvas_drag_start(self, event):
        """Fare sürükleme başladı"""
        self.is_dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    
    def _on_canvas_drag_motion(self, event):
        """Fare sürüklenirken"""
        if not self.is_dragging or not self.current_video_path:
            return
        
        # Fare hareketi hesapla
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        
        # Pozisyonu güncelle
        self.current_pos_x += dx
        self.current_pos_y += dy
        
        # Slider'ları güncelle
        self.pos_x_slider.set(self.current_pos_x)
        self.pos_y_slider.set(self.current_pos_y)
        
        # Başlangıç noktasını güncelle
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        # Preview güncelle
        self._update_editor_preview()
    
    def _on_canvas_drag_end(self, event):
        """Fare sürükleme bitti"""
        self.is_dragging = False
    
    def _on_canvas_scroll(self, event):
        """Fare scroll (Windows/MacOS)"""
        if not self.current_video_path:
            return
        
        # Scroll yönü (1 birimlik hassas zoom)
        delta = 1 if event.delta > 0 else -1
        self._apply_zoom(delta)
    
    def _on_canvas_scroll_linux(self, direction: int):
        """Fare scroll (Linux)"""
        if not self.current_video_path:
            return
        
        self._apply_zoom(direction)  # 1 birimlik hassas zoom
    
    def _apply_zoom(self, delta: int):
        """Zoom uygula"""
        new_scale = max(30, min(300, self.current_scale + delta))
        self.current_scale = new_scale
        self.scale_slider.set(new_scale)
        self._update_editor_preview()
    
    def _on_scale_change(self, value):
        """Scale slider değiştiğinde"""
        self.current_scale = int(value)
        self._update_editor_preview()
    
    def _on_position_change(self, value):
        """Pozisyon slider değiştiğinde"""
        self.current_pos_x = int(self.pos_x_slider.get())
        self.current_pos_y = int(self.pos_y_slider.get())
        self._update_editor_preview()
    
    def _on_bg_mode_change(self):
        """Arka plan modu değiştiğinde"""
        self._update_editor_preview()
    
    def _on_blur_change(self, value):
        """Blur değeri değiştiğinde"""
        self._update_editor_preview()
    
    def _pick_bg_color(self):
        """Arka plan rengi seç"""
        color = colorchooser.askcolor(
            title="Arka Plan Rengi Seç",
            initialcolor=self.bg_color
        )
        if color[1]:
            self.bg_color = color[1]
            self.bg_color_btn.configure(fg_color=self.bg_color, hover_color=self.bg_color)
            self._update_editor_preview()
    
    def _pick_subtitle_color(self):
        """Altyazı rengi seç"""
        color = colorchooser.askcolor(
            title="Altyazı Rengi Seç",
            initialcolor=self.subtitle_color
        )
        if color[1]:
            self.subtitle_color = color[1]
            self.subtitle_color_btn.configure(fg_color=self.subtitle_color, hover_color=self.subtitle_color)
            self._update_subtitle_preview()
    
    def _update_subtitle_preview(self):
        """Altyazı önizlemesini güncelle"""
        # Canvas oluşturulmuş mu kontrol et
        if not hasattr(self, 'subtitle_preview_canvas'):
            return
        
        # Canvas'ı temizle
        self.subtitle_preview_canvas.delete("all")
        
        # Video frame'i varsa göster
        if self.current_video_path and CV2_AVAILABLE:
            photo = self._get_video_frame(0, 320, 180)
            if photo:
                self._sub_preview_photo = photo
                self.subtitle_preview_canvas.create_image(160, 90, image=photo)
        
        # Altyazı pozisyonu
        pos = self.subtitle_position.get()
        if pos == "top":
            y = 30
        elif pos == "center":
            y = 90
        else:  # bottom
            y = 160
        
        # Arka plan
        if hasattr(self, 'subtitle_bg_var') and self.subtitle_bg_var.get():
            self.subtitle_preview_canvas.create_rectangle(
                10, y - 15, 310, y + 15,
                fill="#000000",
                stipple="gray50"
            )
        
        # Altyazı metni
        font_size = int(self.subtitle_fontsize.get()) if hasattr(self, 'subtitle_fontsize') else 16
        self.subtitle_preview_canvas.create_text(
            160, y,
            text="Örnek Altyazı Metni",
            fill=self.subtitle_color if hasattr(self, 'subtitle_color') else "#FFFFFF",
            font=("Arial", font_size, "bold")
        )
    
    def _on_subtitle_style_change(self, value):
        """Altyazı stili değiştiğinde"""
        self._update_subtitle_preview()
    
    # ============================================================
    # THUMBNAIL CALLBACK'LERİ
    # ============================================================
    
    def _on_thumb_effect_change(self, value):
        """Thumbnail efekti değiştiğinde"""
        self._update_thumbnail_with_effects()
    
    def _update_thumbnail_effects(self):
        """Thumbnail efektlerini güncelle"""
        self._update_thumbnail_with_effects()
    
    def _update_thumbnail_with_effects(self):
        """Efektli thumbnail önizlemesi"""
        if not self.current_video_path or not CV2_AVAILABLE:
            return
        
        # Canvas oluşturulmuş mu kontrol et
        if not hasattr(self, 'thumb_canvas'):
            return
        
        time_sec = self.thumb_time.get()
        
        try:
            cap = cv2.VideoCapture(str(self.current_video_path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_num = int(time_sec * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return
            
            # BGR -> RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Boyutlandır
            frame = cv2.resize(frame, (320, 180))
            
            # PIL Image'e çevir
            img = Image.fromarray(frame)
            
            # Parlaklık
            brightness = self.thumb_brightness.get() / 100.0
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(brightness)
            
            # Kontrast
            contrast = self.thumb_contrast.get() / 100.0
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast)
            
            # Doygunluk
            if hasattr(self, 'thumb_saturation'):
                saturation = self.thumb_saturation.get() / 100.0
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(saturation)
            
            # Canvas'a çiz
            photo = ImageTk.PhotoImage(img)
            self._thumb_effect_photo = photo
            
            self.thumb_canvas.delete("all")
            self.thumb_canvas.create_image(160, 90, image=photo)
            
        except Exception as e:
            logger.error(f"Thumbnail efekt hatası: {e}")
    
    def _find_best_frames(self):
        """En iyi frame'leri bul"""
        if not self.current_video_path:
            messagebox.showwarning("Uyarı", "Önce bir video seçin!")
            return
        
        if self.thumbnail_gen:
            try:
                # Önce videoyu yükle
                self.thumbnail_gen.load_video(self.current_video_path)
                
                # En iyi frame'leri bul (num_candidates parametresi)
                candidates = self.thumbnail_gen.find_best_frames(num_candidates=5)
                
                if candidates:
                    # Frame zamanlarını göster
                    times_text = "🎯 Önerilen Zamanlar:\n"
                    for i, candidate in enumerate(candidates[:5], 1):
                        mins = int(candidate.time // 60)
                        secs = int(candidate.time % 60)
                        times_text += f"  {i}. {mins:02d}:{secs:02d} (Skor: {candidate.score:.0f})\n"
                    
                    self.best_frames_label.configure(text=times_text)
                    
                    # İlk frame'e git
                    self.thumb_time.set(candidates[0].time)
                    self._update_thumbnail_with_effects()
                else:
                    self.best_frames_label.configure(text="Frame bulunamadı")
                    
            except Exception as e:
                self.best_frames_label.configure(text=f"Hata: {e}")
                logger.error(f"Best frames hatası: {e}")
        else:
            messagebox.showwarning("Uyarı", "Thumbnail modülü yüklenemedi!")
    
    # ============================================================
    # TRANSFORM KONTROLLERI
    # ============================================================
    
    def _center_video(self):
        """Videoyu ortala"""
        self.current_pos_x = 0
        self.current_pos_y = 0
        self.pos_x_slider.set(0)
        self.pos_y_slider.set(0)
        self._update_editor_preview()
    
    def _fit_video(self):
        """Videoyu sığdır (%100 = tam sığdır)"""
        self.current_scale = 100
        self.scale_slider.set(100)
        self._center_video()
    
    def _fill_video(self):
        """Ekranı doldur (kenarlar kırpılır)"""
        if not self.current_video_info:
            return
        
        # Video ve canvas boyutları
        video_w = self.current_video_info.width
        video_h = self.current_video_info.height
        canvas_w = self.canvas_width
        canvas_h = self.canvas_height
        
        # Fit ve Fill oranları
        fit_scale = min(canvas_w / video_w, canvas_h / video_h)
        fill_scale = max(canvas_w / video_w, canvas_h / video_h)
        
        # Fill için gereken zoom (%100 = fit)
        fill_zoom = int((fill_scale / fit_scale) * 100)
        
        # Slider maksimum değerini kontrol et
        fill_zoom = min(fill_zoom, 200)
        
        self.current_scale = fill_zoom
        self.scale_slider.set(fill_zoom)
        self._center_video()
    
    def _reset_transform(self):
        """Transform sıfırla"""
        self.current_scale = 100
        self.current_pos_x = 0
        self.current_pos_y = 0
        self.scale_slider.set(100)
        self.pos_x_slider.set(0)
        self.pos_y_slider.set(0)
        self._update_editor_preview()
    
    def _start_analysis(self):
        """Akıllı analizi başlat"""
        if not self.current_video_path:
            messagebox.showwarning("Uyarı", "Önce bir video seçin!")
            return
        
        if not self.smart_analyzer:
            messagebox.showerror("Hata", "Akıllı analiz modülü yüklenemedi!")
            return
        
        self.analysis_status.configure(text="Analiz başlatılıyor...")
        self.analysis_progress.set(0)
        
        def worker():
            try:
                self.smart_analyzer.load_video(self.current_video_path)
                
                def progress(pct, msg):
                    self.after(0, lambda p=pct, m=msg: self._update_analysis_progress(p, m))
                
                result = self.smart_analyzer.full_analysis(progress_callback=progress)
                self.after(0, lambda r=result: self._show_analysis_results(r))
                
            except Exception as e:
                error_msg = str(e)
                self.after(0, lambda msg=error_msg: self._analysis_error(msg))
        
        threading.Thread(target=worker, daemon=True).start()
    
    def _update_analysis_progress(self, pct: int, msg: str):
        self.analysis_progress.set(pct / 100)
        self.analysis_status.configure(text=msg)
    
    def _show_analysis_results(self, result):
        self.analysis_progress.set(1)
        self.analysis_status.configure(text="Analiz tamamlandı!")
        
        # Sonucu kaydet
        self.last_analysis_result = result
        
        summary = (
            f"📊 Analiz Özeti\n\n"
            f"• Sessizlik bölümleri: {len(result.silence_segments)}\n"
            f"• Konuşma bölümleri: {len(result.speech_segments)}\n"
            f"• Sahne değişiklikleri: {len(result.scene_changes)}\n"
            f"• Hook adayları: {len(result.hook_candidates)}\n"
            f"• Önerilen kesitler: {len(result.best_segments)}"
        )
        
        if result.best_segments:
            summary += f"\n\n⭐ Önerilen Kesitler:"
            for i, seg in enumerate(result.best_segments[:3], 1):
                mins = int(seg.start // 60)
                secs = int(seg.start % 60)
                dur = seg.end - seg.start
                summary += f"\n   {i}. {mins:02d}:{secs:02d} ({dur:.0f}s) - Skor: {seg.score:.0f}"
            
            # Butonu göster
            self.use_segment_btn.pack(fill="x", pady=(15, 0))
        
        self.analysis_results.configure(text=summary)
    
    def _use_best_segment(self):
        """En iyi kesiti Video Düzenleme'ye uygula"""
        if not self.last_analysis_result or not self.last_analysis_result.best_segments:
            messagebox.showwarning("Uyarı", "Önce analiz yapın!")
            return
        
        best = self.last_analysis_result.best_segments[0]
        
        # Başlangıç zamanını formatla
        start_h = int(best.start // 3600)
        start_m = int((best.start % 3600) // 60)
        start_s = int(best.start % 60)
        
        # Süre hesapla (max 60 saniye)
        duration = min(60, int(best.end - best.start))
        
        # Video Düzenleme sayfasına uygula
        self.start_time_entry.delete(0, "end")
        self.start_time_entry.insert(0, f"{start_h:02d}:{start_m:02d}:{start_s:02d}")
        
        self.duration_entry.delete(0, "end")
        self.duration_entry.insert(0, str(duration))
        
        # Time slider'ı güncelle
        self.time_slider.set(best.start)
        
        # Video Düzenleme sayfasına git
        self._show_page("editor")
        self._update_editor_preview(best.start)
        
        messagebox.showinfo("Uygulandı", 
            f"En iyi kesit ayarlandı:\n"
            f"Başlangıç: {start_h:02d}:{start_m:02d}:{start_s:02d}\n"
            f"Süre: {duration} saniye"
        )
    
    def _analysis_error(self, error: str):
        self.analysis_status.configure(text=f"Hata: {error}")
        messagebox.showerror("Analiz Hatası", error)
    
    def _generate_subtitles(self):
        """Altyazı oluştur"""
        if not self.current_video_path:
            messagebox.showwarning("Uyarı", "Önce bir video seçin!")
            return
        
        if not self.subtitle_gen:
            messagebox.showerror("Hata", "Altyazı modülü yüklenemedi!")
            return
        
        model = self.whisper_model.get()
        
        # Zaman aralığını al
        start_time = 0.0
        duration = None
        
        if hasattr(self, 'subtitle_use_timerange') and self.subtitle_use_timerange.get():
            # Video Düzenleme'den zaman aralığını al
            try:
                start_str = self.start_time_entry.get().strip()
                if start_str:
                    parts = start_str.split(":")
                    if len(parts) == 3:
                        start_time = int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
                    elif len(parts) == 2:
                        start_time = int(parts[0]) * 60 + float(parts[1])
                    else:
                        start_time = float(parts[0])
                
                dur_str = self.duration_entry.get().strip()
                if dur_str:
                    duration = float(dur_str)
                    
                self.subtitle_status.configure(
                    text=f"Zaman aralığı: {start_time:.1f}s - {start_time + (duration or 60):.1f}s"
                )
            except ValueError:
                pass
        
        self.subtitle_status.configure(text=f"Whisper {model} modeli yükleniyor...")
        self.subtitle_progress.set(0.1)
        
        def worker():
            try:
                segments = self.subtitle_gen.generate_subtitles(
                    self.current_video_path,
                    model=model
                )
                
                # Zaman aralığına göre filtrele
                if start_time > 0 or duration:
                    end_time = start_time + (duration or float('inf'))
                    filtered_segments = []
                    for seg in segments:
                        # Segment zaman aralığında mı?
                        if seg.end >= start_time and seg.start <= end_time:
                            # Zamanları offset'le
                            new_seg = type(seg)(
                                start=max(0, seg.start - start_time),
                                end=min(duration or seg.end, seg.end - start_time),
                                text=seg.text
                            )
                            filtered_segments.append(new_seg)
                    segments = filtered_segments
                
                # SRT formatına çevir
                srt_text = ""
                for i, seg in enumerate(segments, 1):
                    start = self._format_srt_time(seg.start)
                    end = self._format_srt_time(seg.end)
                    srt_text += f"{i}\n{start} --> {end}\n{seg.text}\n\n"
                
                self.after(0, lambda text=srt_text: self._show_subtitles(text))
                
            except Exception as e:
                error_msg = str(e)
                self.after(0, lambda msg=error_msg: self._subtitle_error(msg))
        
        threading.Thread(target=worker, daemon=True).start()
    
    def _format_srt_time(self, seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    
    def _show_subtitles(self, srt_text: str):
        self.subtitle_progress.set(1)
        self.subtitle_status.configure(text="Altyazı oluşturuldu!")
        self.subtitle_text.delete("1.0", "end")
        self.subtitle_text.insert("1.0", srt_text)
    
    def _save_subtitle_srt(self):
        """SRT dosyası olarak kaydet"""
        srt_content = self.subtitle_text.get("1.0", "end").strip()
        
        if not srt_content:
            messagebox.showwarning("Uyarı", "Kaydedilecek altyazı yok!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="SRT Dosyası Kaydet",
            defaultextension=".srt",
            filetypes=[("SRT dosyası", "*.srt"), ("Tüm dosyalar", "*.*")],
            initialfile="altyazi.srt"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(srt_content)
                messagebox.showinfo("Başarılı", f"Altyazı kaydedildi:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Hata", f"Kaydetme hatası:\n{e}")
    
    def _copy_subtitles(self):
        """Altyazıyı panoya kopyala"""
        srt_content = self.subtitle_text.get("1.0", "end").strip()
        
        if srt_content:
            self.clipboard_clear()
            self.clipboard_append(srt_content)
            self.subtitle_status.configure(text="✅ Panoya kopyalandı!")
    
    def _subtitle_error(self, error: str):
        self.subtitle_status.configure(text=f"Hata: {error}")
        messagebox.showerror("Altyazı Hatası", error)
    
    def _save_thumbnail(self):
        """Thumbnail kaydet"""
        if not self.current_video_path:
            messagebox.showwarning("Uyarı", "Önce bir video seçin!")
            return
        
        # Dosya kaydetme dialogu
        file_path = filedialog.asksaveasfilename(
            title="Thumbnail Kaydet",
            defaultextension=".png",
            filetypes=[("PNG dosyası", "*.png"), ("JPEG dosyası", "*.jpg")],
            initialfile=f"{self.current_video_path.stem}_thumbnail.png"
        )
        
        if not file_path:
            return
        
        try:
            # Mevcut önizleme frame'ini al
            time_sec = self.thumb_time.get()
            
            if CV2_AVAILABLE:
                cap = cv2.VideoCapture(str(self.current_video_path))
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_num = int(time_sec * fps)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                
                ret, frame = cap.read()
                cap.release()
                
                if ret:
                    # BGR -> RGB
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # YouTube thumbnail boyutu (1280x720)
                    frame = cv2.resize(frame, (1280, 720))
                    
                    # PIL Image'e çevir
                    img = Image.fromarray(frame)
                    
                    # Efektleri uygula
                    brightness = self.thumb_brightness.get() / 100.0
                    contrast = self.thumb_contrast.get() / 100.0
                    saturation = self.thumb_saturation.get() / 100.0 if hasattr(self, 'thumb_saturation') else 1.0
                    
                    img = ImageEnhance.Brightness(img).enhance(brightness)
                    img = ImageEnhance.Contrast(img).enhance(contrast)
                    img = ImageEnhance.Color(img).enhance(saturation)
                    
                    # Başlık metni ekle
                    title_text = self.thumb_title.get().strip()
                    if title_text:
                        from PIL import ImageDraw, ImageFont
                        draw = ImageDraw.Draw(img)
                        try:
                            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
                        except:
                            font = ImageFont.load_default()
                        
                        # Metin boyutunu hesapla
                        bbox = draw.textbbox((0, 0), title_text, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]
                        
                        # Ortala
                        x = (1280 - text_width) // 2
                        y = 720 - text_height - 50
                        
                        # Gölge
                        draw.text((x+3, y+3), title_text, font=font, fill=(0, 0, 0))
                        # Metin
                        draw.text((x, y), title_text, font=font, fill=(255, 255, 255))
                    
                    # Kaydet
                    img.save(file_path)
                    messagebox.showinfo("Başarılı", f"Thumbnail kaydedildi:\n{file_path}")
                else:
                    messagebox.showerror("Hata", "Frame alınamadı!")
            else:
                messagebox.showerror("Hata", "OpenCV yüklü değil!")
                
        except Exception as e:
            messagebox.showerror("Hata", f"Thumbnail kaydedilemedi:\n{e}")
    
    def _generate_seo(self):
        """SEO önerileri oluştur"""
        topic = self.seo_topic.get().strip()
        
        if not topic:
            messagebox.showwarning("Uyarı", "Lütfen bir konu girin!")
            return
        
        # Altyazı varsa transcript olarak kullan
        transcript = ""
        if hasattr(self, 'subtitle_text'):
            srt_content = self.subtitle_text.get("1.0", "end").strip()
            if srt_content:
                # SRT'den sadece metin kısımlarını çıkar
                lines = srt_content.split('\n')
                text_lines = []
                for line in lines:
                    line = line.strip()
                    # Sayı, zaman damgası veya boş satır değilse
                    if line and not line.isdigit() and '-->' not in line:
                        text_lines.append(line)
                transcript = ' '.join(text_lines)
        
        if self.seo_gen:
            self.seo_gen.analyze_content(transcript=transcript, filename=topic)
            suggestion = self.seo_gen.generate_full_suggestion(topic)
            
            self.seo_title.delete(0, "end")
            self.seo_title.insert(0, suggestion.title)
            
            self.seo_hashtags.delete("1.0", "end")
            self.seo_hashtags.insert("1.0", " ".join(suggestion.hashtags))
            
            self.seo_description.delete("1.0", "end")
            self.seo_description.insert("1.0", suggestion.description)
            
            if transcript:
                self.seo_description.insert("end", f"\n\n📝 Transcript:\n{transcript[:200]}...")
        else:
            # Basit öneriler
            self.seo_title.delete(0, "end")
            self.seo_title.insert(0, f"{topic} - Hızlı Rehber 🚀")
            
            self.seo_hashtags.delete("1.0", "end")
            self.seo_hashtags.insert("1.0", "#shorts #viral #tutorial #linux #türkçe")
            
            self.seo_description.delete("1.0", "end")
            self.seo_description.insert("1.0", f"🎯 {topic} hakkında bilmeniz gereken her şey!\n\n👍 Beğenmeyi ve abone olmayı unutma!")
    
    def _copy_seo(self):
        """SEO içeriğini kopyala"""
        title = self.seo_title.get()
        hashtags = self.seo_hashtags.get("1.0", "end").strip()
        desc = self.seo_description.get("1.0", "end").strip()
        
        text = f"{title}\n\n{desc}\n\n{hashtags}"
        
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Kopyalandı", "SEO içeriği panoya kopyalandı!")
    
    def _export_video(self):
        """Video export et"""
        if not self.current_video_path:
            messagebox.showwarning("Uyarı", "Önce bir video seçin!")
            return
        
        if not self.ffmpeg:
            messagebox.showerror("Hata", "FFmpeg modülü yüklenemedi!")
            return
        
        # Parametreleri al
        start_time = self.start_time_entry.get().strip() or "00:00:00"
        duration_str = self.duration_entry.get().strip() or "60"
        
        try:
            duration_sec = int(duration_str)
        except ValueError:
            messagebox.showerror("Hata", "Geçersiz süre değeri!")
            return
        
        # Transform parametreleri
        scale = self.current_scale
        pos_x = self.current_pos_x
        pos_y = self.current_pos_y
        bg_mode = self.bg_mode.get()
        blur_strength = int(self.blur_slider.get())
        crf = int(self.crf_slider.get())
        preset = self.preset_var.get()
        
        # Arka plan rengi
        bg_color = "000000"
        if bg_mode == "color" and hasattr(self, 'bg_color'):
            bg_color = self.bg_color.lstrip('#')
        
        # Altyazı gömme
        burn_subs = self.burn_subtitles.get() if hasattr(self, 'burn_subtitles') else False
        subtitle_srt = ""
        subtitle_style = {}
        
        if burn_subs and hasattr(self, 'subtitle_text'):
            subtitle_srt = self.subtitle_text.get("1.0", "end").strip()
            if subtitle_srt:
                # Altyazı stilini al
                subtitle_style = {
                    'fontsize': int(self.subtitle_fontsize.get()) if hasattr(self, 'subtitle_fontsize') else 20,
                    'color': self.subtitle_color if hasattr(self, 'subtitle_color') else "#FFFFFF",
                    'position': self.subtitle_position.get() if hasattr(self, 'subtitle_position') else "bottom",
                    'bg': self.subtitle_bg_var.get() if hasattr(self, 'subtitle_bg_var') else True
                }
        
        # Çıktı dizini
        output_dir = Path(self.output_dir_var.get()) if hasattr(self, 'output_dir_var') else OUTPUT_DIR
        
        # Export başlat
        self.export_status.configure(text="Export başlatılıyor...")
        self.export_progress.set(0.1)
        
        def worker():
            try:
                # Çıktı dosyası
                output_dir.mkdir(parents=True, exist_ok=True)
                output_name = f"{self.current_video_path.stem}_short.mp4"
                output_path = output_dir / output_name
                
                self.after(0, lambda: self.export_status.configure(text="Video işleniyor..."))
                self.after(0, lambda: self.export_progress.set(0.3))
                
                # Transform ile export
                success = self._export_with_transform(
                    input_path=self.current_video_path,
                    output_path=output_path,
                    start_time=start_time,
                    duration=duration_sec,
                    scale=scale,
                    pos_x=pos_x,
                    pos_y=pos_y,
                    bg_mode=bg_mode,
                    blur_strength=blur_strength,
                    bg_color=bg_color,
                    crf=crf,
                    preset=preset,
                    subtitle_srt=subtitle_srt,
                    subtitle_style=subtitle_style
                )
                
                if success:
                    self.after(0, lambda p=output_path: self._export_complete(p))
                else:
                    self.after(0, lambda: self._export_error("FFmpeg işlemi başarısız"))
                
            except Exception as e:
                error_msg = str(e)
                self.after(0, lambda msg=error_msg: self._export_error(msg))
        
        threading.Thread(target=worker, daemon=True).start()
    
    def _export_with_transform(
        self,
        input_path: Path,
        output_path: Path,
        start_time: str,
        duration: int,
        scale: int,
        pos_x: int,
        pos_y: int,
        bg_mode: str,
        blur_strength: int,
        bg_color: str,
        crf: int,
        preset: str,
        subtitle_srt: str = "",
        subtitle_style: dict = None
    ) -> bool:
        """Transform uygulanmış video export et"""
        import subprocess
        import tempfile
        
        # Output boyutları (9:16 shorts formatı)
        out_w = 1080
        out_h = 1920
        
        # Kullanıcının zoom değeri (scale %100 = fit to canvas)
        zoom_factor = scale / 100.0
        
        # FIT SCALE: Videoyu canvas'a sığdırmak için FFmpeg expression
        # min(out_w/iw, out_h/ih) = fit scale
        # Sonra zoom_factor ile çarp
        fit_scale_expr = f"min({out_w}/iw\\,{out_h}/ih)*{zoom_factor}"
        
        # Pozisyon (preview'daki pozisyonu export boyutuna ölçekle)
        # Preview canvas: 320x568, Export canvas: 1080x1920
        pos_scale_x = out_w / 320
        pos_scale_y = out_h / 568
        export_pos_x = int(pos_x * pos_scale_x)
        export_pos_y = int(pos_y * pos_scale_y)
        
        # Geçici SRT dosyası (altyazı varsa)
        temp_srt_path = None
        if subtitle_srt:
            try:
                fd, temp_srt_path = tempfile.mkstemp(suffix='.srt')
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    f.write(subtitle_srt)
            except Exception as e:
                logger.error(f"SRT dosyası oluşturulamadı: {e}")
                temp_srt_path = None
        
        # Arka plan modu
        if bg_mode == "blur":
            blur_val = blur_strength if blur_strength % 2 == 1 else blur_strength + 1
            filter_complex = (
                # Arka plan: video'yu canvas boyutuna scale et (crop ile doldur), sonra blur
                f"[0:v]scale={out_w}:{out_h}:force_original_aspect_ratio=increase,"
                f"crop={out_w}:{out_h},boxblur={blur_val}:1[bg];"
                # Ön plan: video'yu fit scale ile boyutlandır
                f"[0:v]scale='trunc(iw*{fit_scale_expr}/2)*2':'trunc(ih*{fit_scale_expr}/2)*2'[fg];"
                # Overlay: ön planı arka planın üzerine koy
                f"[bg][fg]overlay=(W-w)/2+{export_pos_x}:(H-h)/2+{export_pos_y}[out]"
            )
        elif bg_mode == "color":
            filter_complex = (
                f"color=c=#{bg_color}:s={out_w}x{out_h}:d={duration}[bg];"
                f"[0:v]scale='trunc(iw*{fit_scale_expr}/2)*2':'trunc(ih*{fit_scale_expr}/2)*2'[fg];"
                f"[bg][fg]overlay=(W-w)/2+{export_pos_x}:(H-h)/2+{export_pos_y}:shortest=1[out]"
            )
        else:  # black
            filter_complex = (
                f"color=c=black:s={out_w}x{out_h}:d={duration}[bg];"
                f"[0:v]scale='trunc(iw*{fit_scale_expr}/2)*2':'trunc(ih*{fit_scale_expr}/2)*2'[fg];"
                f"[bg][fg]overlay=(W-w)/2+{export_pos_x}:(H-h)/2+{export_pos_y}:shortest=1[out]"
            )
        
        # Output stream adı
        output_stream = "[out]"
        
        # Altyazı varsa filter'a ekle
        if temp_srt_path and subtitle_style:
            fontsize = subtitle_style.get('fontsize', 20) * 3  # 1080p için 3x
            color = subtitle_style.get('color', '#FFFFFF').lstrip('#')
            position = subtitle_style.get('position', 'bottom')
            
            if position == 'top':
                margin_v = 80
                alignment = 6  # top-center
            elif position == 'center':
                margin_v = 0
                alignment = 5  # center
            else:  # bottom
                margin_v = 80
                alignment = 2  # bottom-center
            
            escaped_srt = temp_srt_path.replace('\\', '/').replace(':', '\\:')
            filter_complex += f";[out]subtitles='{escaped_srt}':force_style='FontSize={fontsize},PrimaryColour=&H{color}&,Alignment={alignment},MarginV={margin_v}'[final]"
            output_stream = "[final]"
        
        # FFmpeg komutu
        cmd = [
            "ffmpeg",
            "-ss", start_time,
            "-i", str(input_path),
            "-t", str(duration),
            "-filter_complex", filter_complex,
            "-map", output_stream,
            "-map", "0:a?",  # Ses varsa ekle
            "-c:v", "libx264",
            "-preset", preset,
            "-crf", str(crf),
            "-c:a", "aac",
            "-b:a", "128k",
            "-y",
            str(output_path)
        ]
        
        try:
            logger.info(f"FFmpeg komutu: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg hatası: {result.stderr}")
                # Altyazısız tekrar dene
                if temp_srt_path:
                    logger.info("Altyazısız tekrar deneniyor...")
                    return self._export_with_transform(
                        input_path, output_path, start_time, duration,
                        scale, pos_x, pos_y, bg_mode, blur_strength,
                        bg_color, crf, preset, "", None
                    )
                return False
            
            return output_path.exists()
            
        except Exception as e:
            logger.error(f"Export hatası: {e}")
            return False
        
        finally:
            # Geçici SRT dosyasını sil
            if temp_srt_path and os.path.exists(temp_srt_path):
                try:
                    os.remove(temp_srt_path)
                except:
                    pass
    
    def _select_output_dir(self):
        """Çıktı dizini seç"""
        dir_path = filedialog.askdirectory(
            title="Çıktı Dizini Seç",
            initialdir=self.output_dir_var.get() if hasattr(self, 'output_dir_var') else str(OUTPUT_DIR)
        )
        if dir_path:
            self.output_dir_var.set(dir_path)
    
    def _export_complete(self, output_path: Path):
        self.export_progress.set(1)
        self.export_status.configure(text=f"✅ Tamamlandı: {output_path.name}")
        
        # Dosya yolunu göster
        result = messagebox.askyesno(
            "Başarılı", 
            f"Video oluşturuldu:\n{output_path}\n\nDosya konumunu açmak ister misiniz?"
        )
        if result:
            import subprocess
            subprocess.run(["xdg-open", str(output_path.parent)])
    
    def _export_error(self, error: str):
        self.export_progress.set(0)
        self.export_status.configure(text=f"❌ Hata: {error}")
        messagebox.showerror("Export Hatası", error)


# ============================================================
# MAIN
# ============================================================

def main():
    """Ana fonksiyon"""
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
