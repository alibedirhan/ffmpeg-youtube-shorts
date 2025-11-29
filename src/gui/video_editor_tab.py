"""
LinuxShorts Generator - Professional Video Editor GUI v2.0
Modern, kullanıcı dostu, scroll destekli YouTube Shorts editörü
"""

import customtkinter as ctk
from tkinter import Canvas, messagebox, colorchooser
from PIL import Image, ImageTk
from pathlib import Path
from typing import Optional, Callable
import time
import threading

from utils.logger import get_logger

logger = get_logger("LinuxShorts.EditorTab")

# OpenCV kontrolü
try:
    from core.video_editor import ProVideoEditor, VideoTransform
    OPENCV_AVAILABLE = True
except ImportError as e:
    OPENCV_AVAILABLE = False
    logger.warning(f"OpenCV bulunamadı: {e}")


class ModernSlider(ctk.CTkFrame):
    """Modern slider + entry + label kombinasyonu"""
    
    def __init__(
        self,
        parent,
        label: str,
        from_: float,
        to_: float,
        default: float,
        step: float = 1.0,
        unit: str = "",
        command: Optional[Callable] = None
    ):
        super().__init__(parent, fg_color="transparent")
        
        self.from_ = from_
        self.to_ = to_
        self.step = step
        self.unit = unit
        self.command = command
        self._updating = False
        
        # Üst satır - Label ve Entry
        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 4))
        
        self.label = ctk.CTkLabel(
            top_row,
            text=label,
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.label.pack(side="left")
        
        # Entry + Unit sağda
        entry_frame = ctk.CTkFrame(top_row, fg_color="transparent")
        entry_frame.pack(side="right")
        
        self.entry = ctk.CTkEntry(
            entry_frame, 
            width=55, 
            height=26,
            font=ctk.CTkFont(size=11),
            justify="center"
        )
        self.entry.pack(side="left")
        self.entry.insert(0, str(int(default) if step >= 1 else f"{default:.1f}"))
        self.entry.bind("<Return>", self._on_entry_change)
        self.entry.bind("<FocusOut>", self._on_entry_change)
        
        if unit:
            ctk.CTkLabel(
                entry_frame,
                text=unit,
                font=ctk.CTkFont(size=10),
                text_color="gray",
                width=20
            ).pack(side="left", padx=(2, 0))
        
        # Alt satır - Slider
        self.slider = ctk.CTkSlider(
            self,
            from_=from_,
            to=to_,
            number_of_steps=int((to_ - from_) / step) if step > 0 else 100,
            command=self._on_slider_change,
            height=16
        )
        self.slider.set(default)
        self.slider.pack(fill="x")
    
    def _on_slider_change(self, value):
        if self._updating:
            return
        self._updating = True
        
        display = str(int(value)) if self.step >= 1 else f"{value:.1f}"
        self.entry.delete(0, "end")
        self.entry.insert(0, display)
        
        if self.command:
            self.command(value)
        
        self._updating = False
    
    def _on_entry_change(self, event=None):
        if self._updating:
            return
        self._updating = True
        
        try:
            value = float(self.entry.get())
            value = max(self.from_, min(self.to_, value))
            self.slider.set(value)
            
            if self.command:
                self.command(value)
        except ValueError:
            pass
        
        self._updating = False
    
    def get(self) -> float:
        return self.slider.get()
    
    def set(self, value: float):
        self._updating = True
        self.slider.set(value)
        display = str(int(value)) if self.step >= 1 else f"{value:.1f}"
        self.entry.delete(0, "end")
        self.entry.insert(0, display)
        self._updating = False


class CollapsibleSection(ctk.CTkFrame):
    """Açılıp kapanabilen bölüm"""
    
    def __init__(self, parent, title: str, icon: str = "", expanded: bool = True):
        super().__init__(parent, fg_color=("gray92", "gray14"), corner_radius=10)
        
        self.expanded = expanded
        self.title = title
        self.icon = icon
        
        # Başlık butonu
        self.header = ctk.CTkButton(
            self,
            text=f"{'▼' if expanded else '▶'} {icon} {title}",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="transparent",
            hover_color=("gray80", "gray25"),
            anchor="w",
            command=self._toggle,
            height=35
        )
        self.header.pack(fill="x", padx=5, pady=(5, 0))
        
        # İçerik container
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        if expanded:
            self.content.pack(fill="x", padx=15, pady=(5, 15))
    
    def _toggle(self):
        self.expanded = not self.expanded
        arrow = "▼" if self.expanded else "▶"
        self.header.configure(text=f"{arrow} {self.icon} {self.title}")
        
        if self.expanded:
            self.content.pack(fill="x", padx=15, pady=(5, 15))
        else:
            self.content.pack_forget()
    
    def get_content(self) -> ctk.CTkFrame:
        return self.content


class VideoEditorTab:
    """Profesyonel YouTube Shorts Video Editörü v2.0"""
    
    def __init__(
        self,
        parent_tab: ctk.CTkFrame,
        on_export_callback: Optional[Callable] = None
    ):
        self.parent = parent_tab
        self.on_export = on_export_callback
        
        self.editor: Optional[ProVideoEditor] = None
        if OPENCV_AVAILABLE:
            self.editor = ProVideoEditor()
        
        # Canvas boyutları
        self.canvas_width = 270
        self.canvas_height = 480
        self.preview_image: Optional[ImageTk.PhotoImage] = None
        
        # State
        self.video_loaded = False
        self.video_path: Optional[Path] = None
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        self._create_ui()
        logger.info("VideoEditorTab v2.0 oluşturuldu")
    
    def _create_ui(self):
        """Ana UI yapısı - Scrollable"""
        
        if not OPENCV_AVAILABLE:
            self._show_opencv_warning()
            return
        
        # Ana scrollable container
        self.main_scroll = ctk.CTkScrollableFrame(
            self.parent,
            fg_color="transparent"
        )
        self.main_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # İçerik için ana frame
        content = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        content.pack(fill="both", expand=True)
        
        # 2 sütunlu layout
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        
        # SOL SÜTUN - Preview ve Timeline
        left_col = ctk.CTkFrame(content, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self._create_preview_section(left_col)
        self._create_timeline_section(left_col)
        
        # SAĞ SÜTUN - Tüm Ayarlar
        right_col = ctk.CTkFrame(content, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew")
        
        self._create_transform_section(right_col)
        self._create_background_section(right_col)
        self._create_quality_section(right_col)
        self._create_suggestions_section(right_col)
        self._create_export_section(right_col)
    
    def _show_opencv_warning(self):
        """OpenCV yok uyarısı"""
        frame = ctk.CTkFrame(self.parent)
        frame.pack(expand=True, pady=50)
        
        ctk.CTkLabel(
            frame,
            text="⚠️ OpenCV Gerekli",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="orange"
        ).pack(pady=20, padx=40)
        
        ctk.CTkLabel(
            frame,
            text="pip install opencv-python",
            font=ctk.CTkFont(size=14, family="monospace")
        ).pack(pady=10, padx=40)
    
    def _create_preview_section(self, parent):
        """Önizleme bölümü"""
        section = ctk.CTkFrame(parent, fg_color=("gray92", "gray14"), corner_radius=10)
        section.pack(fill="x", pady=(0, 10))
        
        # Başlık
        header = ctk.CTkFrame(section, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(
            header,
            text="📱 Önizleme",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")
        
        self.resolution_label = ctk.CTkLabel(
            header,
            text="1080 × 1920",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.resolution_label.pack(side="right")
        
        # Canvas container
        canvas_container = ctk.CTkFrame(section, fg_color="transparent")
        canvas_container.pack(pady=10)
        
        self.canvas = Canvas(
            canvas_container,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#0f0f1a",
            highlightthickness=2,
            highlightbackground="#3498db"
        )
        self.canvas.pack()
        
        # Canvas events
        self.canvas.bind("<ButtonPress-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_drag_end)
        self.canvas.bind("<MouseWheel>", self._on_canvas_scroll)
        self.canvas.bind("<Button-4>", lambda e: self._on_scroll_dir(1))
        self.canvas.bind("<Button-5>", lambda e: self._on_scroll_dir(-1))
        
        # Placeholder
        self.canvas.create_text(
            self.canvas_width // 2,
            self.canvas_height // 2,
            text="🎬\n\nVideo yüklemek için\nsol panelden seçin",
            fill="#555",
            font=("Arial", 11),
            justify="center",
            tags="placeholder"
        )
        
        # İpuçları
        ctk.CTkLabel(
            section,
            text="🖱️ Sürükle: Pozisyon  •  🔄 Scroll: Zoom",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(pady=(0, 10))
        
        # Görünüm checkbox'ları
        view_frame = ctk.CTkFrame(section, fg_color="transparent")
        view_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        self.show_safe_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            view_frame,
            text="Güvenli Alan",
            variable=self.show_safe_var,
            command=self._on_overlay_change,
            font=ctk.CTkFont(size=10),
            checkbox_width=18,
            checkbox_height=18
        ).pack(side="left", padx=(0, 15))
        
        self.show_grid_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            view_frame,
            text="Grid",
            variable=self.show_grid_var,
            command=self._on_overlay_change,
            font=ctk.CTkFont(size=10),
            checkbox_width=18,
            checkbox_height=18
        ).pack(side="left", padx=(0, 15))
        
        self.show_center_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            view_frame,
            text="Merkez",
            variable=self.show_center_var,
            command=self._on_overlay_change,
            font=ctk.CTkFont(size=10),
            checkbox_width=18,
            checkbox_height=18
        ).pack(side="left")
    
    def _create_timeline_section(self, parent):
        """Timeline bölümü"""
        section = ctk.CTkFrame(parent, fg_color=("gray92", "gray14"), corner_radius=10)
        section.pack(fill="x", pady=(0, 10))
        
        inner = ctk.CTkFrame(section, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            inner,
            text="⏱️ Zaman Çizelgesi",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 8))
        
        self.time_slider = ctk.CTkSlider(
            inner,
            from_=0,
            to=100,
            command=self._on_time_change,
            height=18
        )
        self.time_slider.set(0)
        self.time_slider.pack(fill="x", pady=(0, 5))
        
        self.time_label = ctk.CTkLabel(
            inner,
            text="00:00 / 00:00",
            font=ctk.CTkFont(size=12, family="monospace")
        )
        self.time_label.pack(anchor="e")
    
    def _create_transform_section(self, parent):
        """Transform ayarları"""
        section = CollapsibleSection(parent, "Transform", "📐", expanded=True)
        section.pack(fill="x", pady=(0, 8))
        content = section.get_content()
        
        self.scale_slider = ModernSlider(
            content, label="Ölçek (Zoom)", from_=30, to_=300,
            default=100, step=5, unit="%", command=self._on_scale_change
        )
        self.scale_slider.pack(fill="x", pady=(0, 10))
        
        self.pos_x_slider = ModernSlider(
            content, label="X Pozisyon", from_=-500, to_=500,
            default=0, step=10, unit="px", command=self._on_pos_x_change
        )
        self.pos_x_slider.pack(fill="x", pady=(0, 10))
        
        self.pos_y_slider = ModernSlider(
            content, label="Y Pozisyon", from_=-500, to_=500,
            default=0, step=10, unit="px", command=self._on_pos_y_change
        )
        self.pos_y_slider.pack(fill="x", pady=(0, 10))
        
        # Hızlı butonlar
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        for text, cmd in [("⊙ Ortala", self._center_video), 
                          ("↔ Sığdır", self._fit_width), 
                          ("↺ Sıfırla", self._reset_transform)]:
            ctk.CTkButton(
                btn_frame, text=text, width=80, height=28, command=cmd,
                fg_color=("gray75", "gray30"), hover_color=("gray65", "gray40"),
                font=ctk.CTkFont(size=11)
            ).pack(side="left", padx=(0, 5))
    
    def _create_background_section(self, parent):
        """Arka plan ayarları"""
        section = CollapsibleSection(parent, "Arka Plan", "🎨", expanded=True)
        section.pack(fill="x", pady=(0, 8))
        content = section.get_content()
        
        self.bg_mode_var = ctk.StringVar(value="blur")
        
        modes_frame = ctk.CTkFrame(content, fg_color="transparent")
        modes_frame.pack(fill="x", pady=(0, 10))
        
        for icon, value, tooltip in [("⬛", "black", "Siyah"), ("🌫️", "blur", "Blur"),
                                      ("🌈", "gradient", "Gradient"), ("🎨", "color", "Renk")]:
            ctk.CTkRadioButton(
                modes_frame, text=f"{icon} {tooltip}", variable=self.bg_mode_var,
                value=value, command=self._on_bg_mode_change,
                font=ctk.CTkFont(size=11), radiobutton_width=16, radiobutton_height=16
            ).pack(side="left", padx=(0, 10))
        
        # Blur ayarları
        self.blur_frame = ctk.CTkFrame(content, fg_color=("gray88", "gray20"), corner_radius=8)
        self.blur_frame.pack(fill="x", pady=(0, 5))
        
        blur_inner = ctk.CTkFrame(self.blur_frame, fg_color="transparent")
        blur_inner.pack(fill="x", padx=10, pady=8)
        
        ctk.CTkLabel(blur_inner, text="Blur Gücü", font=ctk.CTkFont(size=11)).pack(side="left")
        
        self.blur_slider = ctk.CTkSlider(
            blur_inner, from_=5, to=50, number_of_steps=45,
            command=self._on_blur_change, width=120
        )
        self.blur_slider.set(25)
        self.blur_slider.pack(side="right")
        
        # Renk ayarları
        self.color_frame = ctk.CTkFrame(content, fg_color=("gray88", "gray20"), corner_radius=8)
        color_inner = ctk.CTkFrame(self.color_frame, fg_color="transparent")
        color_inner.pack(fill="x", padx=10, pady=8)
        ctk.CTkLabel(color_inner, text="Arka Plan Rengi", font=ctk.CTkFont(size=11)).pack(side="left")
        self.color_btn = ctk.CTkButton(
            color_inner, text="", width=40, height=25, fg_color="#1a1a2e",
            command=self._pick_bg_color, corner_radius=4
        )
        self.color_btn.pack(side="right")
        
        # Gradient ayarları
        self.gradient_frame = ctk.CTkFrame(content, fg_color=("gray88", "gray20"), corner_radius=8)
        grad_inner = ctk.CTkFrame(self.gradient_frame, fg_color="transparent")
        grad_inner.pack(fill="x", padx=10, pady=8)
        ctk.CTkLabel(grad_inner, text="Gradient", font=ctk.CTkFont(size=11)).pack(side="left")
        
        grad_btns = ctk.CTkFrame(grad_inner, fg_color="transparent")
        grad_btns.pack(side="right")
        
        self.grad_start_btn = ctk.CTkButton(
            grad_btns, text="Üst", width=50, height=25, fg_color="#1a1a2e",
            command=lambda: self._pick_gradient_color("start"), font=ctk.CTkFont(size=10)
        )
        self.grad_start_btn.pack(side="left", padx=(0, 5))
        
        self.grad_end_btn = ctk.CTkButton(
            grad_btns, text="Alt", width=50, height=25, fg_color="#16213e",
            command=lambda: self._pick_gradient_color("end"), font=ctk.CTkFont(size=10)
        )
        self.grad_end_btn.pack(side="left")
    
    def _create_quality_section(self, parent):
        """Kalite ayarları"""
        section = CollapsibleSection(parent, "Kalite", "⚙️", expanded=False)
        section.pack(fill="x", pady=(0, 8))
        content = section.get_content()
        
        self.crf_slider = ModernSlider(
            content, label="CRF (Kalite)", from_=18, to_=28,
            default=23, step=1, unit="", command=self._on_crf_change
        )
        self.crf_slider.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(
            content, text="18 = Yüksek kalite  •  28 = Küçük dosya",
            font=ctk.CTkFont(size=9), text_color="gray"
        ).pack(anchor="w", pady=(0, 10))
        
        preset_frame = ctk.CTkFrame(content, fg_color="transparent")
        preset_frame.pack(fill="x")
        
        ctk.CTkLabel(preset_frame, text="Kodlama Hızı", font=ctk.CTkFont(size=12)).pack(side="left")
        
        self.preset_var = ctk.StringVar(value="medium")
        self.preset_menu = ctk.CTkOptionMenu(
            preset_frame, values=["ultrafast", "fast", "medium", "slow"],
            variable=self.preset_var, command=self._on_preset_change,
            width=110, height=28, font=ctk.CTkFont(size=11)
        )
        self.preset_menu.pack(side="right")
    
    def _create_suggestions_section(self, parent):
        """Otomatik kesit önerileri"""
        section = CollapsibleSection(parent, "Otomatik Kesit", "✨", expanded=False)
        section.pack(fill="x", pady=(0, 8))
        content = section.get_content()
        
        ctk.CTkLabel(
            content, text="Videoyu eşit parçalara böl, istediğini seç",
            font=ctk.CTkFont(size=10), text_color="gray"
        ).pack(anchor="w", pady=(0, 8))
        
        ctrl_frame = ctk.CTkFrame(content, fg_color="transparent")
        ctrl_frame.pack(fill="x", pady=(0, 8))
        
        ctk.CTkLabel(ctrl_frame, text="Süre:", font=ctk.CTkFont(size=11)).pack(side="left")
        self.seg_duration_entry = ctk.CTkEntry(ctrl_frame, width=50, height=26)
        self.seg_duration_entry.insert(0, "60")
        self.seg_duration_entry.pack(side="left", padx=(5, 15))
        
        ctk.CTkLabel(ctrl_frame, text="Adet:", font=ctk.CTkFont(size=11)).pack(side="left")
        self.seg_count_entry = ctk.CTkEntry(ctrl_frame, width=40, height=26)
        self.seg_count_entry.insert(0, "5")
        self.seg_count_entry.pack(side="left", padx=(5, 0))
        
        ctk.CTkButton(
            content, text="🔍 Önerileri Oluştur", command=self._generate_suggestions,
            height=32, font=ctk.CTkFont(size=12)
        ).pack(fill="x", pady=(0, 8))
        
        self.suggestions_frame = ctk.CTkFrame(content, fg_color=("gray88", "gray20"), corner_radius=8)
        self.suggestions_frame.pack(fill="x")
        
        self.suggestions_status = ctk.CTkLabel(
            self.suggestions_frame, text="Öneri oluşturmak için butona tıklayın",
            font=ctk.CTkFont(size=10), text_color="gray"
        )
        self.suggestions_status.pack(pady=10)
    
    def _create_export_section(self, parent):
        """Export bölümü"""
        section = ctk.CTkFrame(parent, fg_color=("gray92", "gray14"), corner_radius=10)
        section.pack(fill="x", pady=(5, 0))
        
        inner = ctk.CTkFrame(section, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            inner, text="🎬 Export", font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 10))
        
        dur_frame = ctk.CTkFrame(inner, fg_color="transparent")
        dur_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(dur_frame, text="Süre (saniye):", font=ctk.CTkFont(size=12)).pack(side="left")
        
        self.duration_entry = ctk.CTkEntry(dur_frame, width=60, height=28)
        self.duration_entry.insert(0, "60")
        self.duration_entry.pack(side="left", padx=10)
        
        ctk.CTkLabel(dur_frame, text="(max 60)", font=ctk.CTkFont(size=10), text_color="gray").pack(side="left")
        
        self.export_btn = ctk.CTkButton(
            inner, text="🚀 Short Oluştur", command=self._export_video,
            height=45, font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#27ae60", hover_color="#229954"
        )
        self.export_btn.pack(fill="x", pady=(0, 5))
        
        self.status_label = ctk.CTkLabel(inner, text="", font=ctk.CTkFont(size=11), text_color="gray")
        self.status_label.pack()
    
    # EVENT HANDLERS
    def _on_bg_mode_change(self):
        mode = self.bg_mode_var.get()
        self.blur_frame.pack_forget()
        self.color_frame.pack_forget()
        self.gradient_frame.pack_forget()
        
        if mode == "blur":
            self.blur_frame.pack(fill="x", pady=(0, 5))
        elif mode == "color":
            self.color_frame.pack(fill="x", pady=(0, 5))
        elif mode == "gradient":
            self.gradient_frame.pack(fill="x", pady=(0, 5))
        
        if self.editor:
            self.editor.set_background_mode(mode)
            self._update_preview()
    
    def _on_blur_change(self, value):
        if self.editor:
            self.editor.set_blur_strength(int(value))
            self._update_preview()
    
    def _pick_bg_color(self):
        color = colorchooser.askcolor(title="Arka Plan Rengi")
        if color[1]:
            self.color_btn.configure(fg_color=color[1])
            if self.editor:
                self.editor.set_background_color(color[1])
                self._update_preview()
    
    def _pick_gradient_color(self, which: str):
        color = colorchooser.askcolor(title=f"Gradient {'Üst' if which == 'start' else 'Alt'} Rengi")
        if color[1]:
            if which == "start":
                self.grad_start_btn.configure(fg_color=color[1])
            else:
                self.grad_end_btn.configure(fg_color=color[1])
            
            if self.editor:
                start = self.grad_start_btn.cget("fg_color")
                end = self.grad_end_btn.cget("fg_color")
                self.editor.set_gradient_colors(start, end)
                self._update_preview()
    
    def _on_overlay_change(self):
        if self.editor:
            self.editor.show_safe_zone = self.show_safe_var.get()
            self.editor.show_grid = self.show_grid_var.get()
            self.editor.show_center_lines = self.show_center_var.get()
            self._update_preview()
    
    def _on_scale_change(self, value):
        if self.editor:
            self.editor.set_scale(value)
            self._update_preview()
    
    def _on_pos_x_change(self, value):
        if self.editor:
            self.editor.set_position(int(value), self.editor.transform.pos_y)
            self._update_preview()
    
    def _on_pos_y_change(self, value):
        if self.editor:
            self.editor.set_position(self.editor.transform.pos_x, int(value))
            self._update_preview()
    
    def _on_time_change(self, value):
        if not self.video_loaded or not self.editor:
            return
        self.editor.update_frame(value)
        info = self.editor.video_info
        if info:
            self.time_label.configure(text=f"{self._format_time(value)} / {self._format_time(info['duration'])}")
        self._update_preview()
    
    def _on_crf_change(self, value):
        if self.editor:
            self.editor.set_quality(int(value), self.preset_var.get())
    
    def _on_preset_change(self, value):
        if self.editor:
            self.editor.set_quality(int(self.crf_slider.get()), value)
    
    def _on_drag_start(self, event):
        self.is_dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    
    def _on_drag_motion(self, event):
        if not self.is_dragging or not self.editor:
            return
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        scale = self.editor.transform.output_width / self.canvas_width
        new_x = self.editor.transform.pos_x + int(dx * scale)
        new_y = self.editor.transform.pos_y + int(dy * scale)
        self.editor.set_position(new_x, new_y)
        self.pos_x_slider.set(new_x)
        self.pos_y_slider.set(new_y)
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self._update_preview()
    
    def _on_drag_end(self, event):
        self.is_dragging = False
    
    def _on_canvas_scroll(self, event):
        delta = 1 if event.delta > 0 else -1
        self._on_scroll_dir(delta)
    
    def _on_scroll_dir(self, direction: int):
        if not self.editor:
            return
        current = self.editor.transform.scale
        new_scale = max(30, min(300, current + direction * 10))
        self.editor.set_scale(new_scale)
        self.scale_slider.set(new_scale)
        self._update_preview()
    
    def _center_video(self):
        if self.editor:
            self.editor.center_video()
            self.pos_x_slider.set(0)
            self.pos_y_slider.set(0)
            self._update_preview()
            self.status_label.configure(text="✓ Ortalandı")
    
    def _fit_width(self):
        if self.editor:
            self.editor.fit_to_width()
            self.scale_slider.set(self.editor.transform.scale)
            self._update_preview()
            self.status_label.configure(text="✓ Genişliğe sığdırıldı")
    
    def _reset_transform(self):
        if self.editor:
            self.editor.reset_transform()
            self.scale_slider.set(100)
            self.pos_x_slider.set(0)
            self.pos_y_slider.set(0)
            self._update_preview()
            self.status_label.configure(text="✓ Sıfırlandı")
    
    def _generate_suggestions(self):
        if not self.editor or not self.video_loaded:
            messagebox.showwarning("Uyarı", "Önce bir video yükleyin!")
            return
        
        try:
            duration = float(self.seg_duration_entry.get() or "60")
            count = int(self.seg_count_entry.get() or "5")
        except ValueError:
            duration, count = 60, 5
        
        segments = self.editor.suggest_segments(segment_length=duration, max_segments=count)
        
        for widget in self.suggestions_frame.winfo_children():
            widget.destroy()
        
        if not segments:
            ctk.CTkLabel(
                self.suggestions_frame, text="Öneri bulunamadı",
                font=ctk.CTkFont(size=10), text_color="gray"
            ).pack(pady=10)
            return
        
        for seg in segments:
            row = ctk.CTkFrame(self.suggestions_frame, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=3)
            
            start, dur = seg['start'], seg['duration']
            ctk.CTkLabel(
                row, text=f"#{seg['index']} {self._format_time(start)} → {self._format_time(start + dur)}",
                font=ctk.CTkFont(size=10), anchor="w"
            ).pack(side="left", fill="x", expand=True)
            
            ctk.CTkButton(
                row, text="Seç", width=45, height=22,
                command=lambda s=start, d=dur: self._apply_suggestion(s, d),
                font=ctk.CTkFont(size=10)
            ).pack(side="right")
        
        ctk.CTkLabel(
            self.suggestions_frame, text=f"{len(segments)} öneri bulundu",
            font=ctk.CTkFont(size=9), text_color="gray"
        ).pack(pady=(5, 8))
    
    def _apply_suggestion(self, start: float, duration: float):
        if not self.editor:
            return
        self.time_slider.set(start)
        self.duration_entry.delete(0, "end")
        self.duration_entry.insert(0, str(int(duration)))
        self._on_time_change(start)
        self.status_label.configure(text="✅ Öneri uygulandı")
    
    # VIDEO METHODS
    def load_video(self, video_path: Path) -> bool:
        if not OPENCV_AVAILABLE or not self.editor:
            return False
        try:
            if not self.editor.load_video(video_path):
                return False
            self.video_path = video_path
            self.video_loaded = True
            info = self.editor.video_info
            if info:
                self.time_slider.configure(to=info['duration'])
                self.editor.preview_width = self.canvas_width
                self.editor.preview_height = self.canvas_height
            self.canvas.delete("placeholder")
            self._update_preview()
            return True
        except Exception as e:
            logger.error(f"Video yükleme hatası: {e}")
            return False
    
    def _update_preview(self):
        if not self.video_loaded or not self.editor:
            return
        try:
            preview = self.editor.get_preview_image()
            if preview is None:
                return
            self.preview_image = ImageTk.PhotoImage(preview)
            self.canvas.delete("all")
            self.canvas.create_image(
                self.canvas_width // 2, self.canvas_height // 2,
                image=self.preview_image, anchor="center"
            )
        except Exception as e:
            logger.error(f"Preview hatası: {e}")
    
    def _format_time(self, seconds: float) -> str:
        return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}"
    
    def _export_video(self):
        if not self.video_loaded or not self.editor:
            messagebox.showerror("Hata", "Önce video yükleyin!")
            return
        
        try:
            duration = min(60, float(self.duration_entry.get() or "60"))
        except:
            duration = 60
        
        start_time = self.time_slider.get()
        info = self.editor.video_info
        if info:
            duration = min(duration, info['duration'] - start_time)
        
        timestamp = int(time.time())
        output_name = f"short_{self.video_path.stem}_{timestamp}.mp4"
        
        from utils.config import OUTPUT_DIR
        output_path = OUTPUT_DIR / output_name
        
        self.export_btn.configure(state="disabled", text="⏳ İşleniyor...")
        self.status_label.configure(text="Export başladı...")
        
        def worker():
            success = self.editor.export_short(
                output_path=output_path, start_time=start_time, duration=duration
            )
            self.parent.after(0, lambda: self._export_done(success, output_path))
        
        threading.Thread(target=worker, daemon=True).start()
    
    def _export_done(self, success: bool, output_path: Path):
        self.export_btn.configure(state="normal", text="🚀 Short Oluştur")
        if success:
            size = output_path.stat().st_size / (1024*1024)
            self.status_label.configure(text=f"✅ Tamamlandı! ({size:.1f} MB)")
            if messagebox.askyesno("🎉 Başarılı!", f"Short oluşturuldu!\n\n{output_path.name}\n\nKlasörü açmak ister misiniz?"):
                import subprocess
                subprocess.run(["xdg-open", str(output_path.parent)])
            if self.on_export:
                self.on_export(output_path)
        else:
            self.status_label.configure(text="❌ Export başarısız!")
            messagebox.showerror("Hata", "Export sırasında bir hata oluştu!")
