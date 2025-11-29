"""
LinuxShorts Pro - Profesyonel Sekmeler
Akıllı Analiz, Thumbnail, SEO, Preset Yönetimi
"""

from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox, filedialog
from pathlib import Path
from typing import Optional, Callable, List, TYPE_CHECKING
import threading

from utils.logger import get_logger

logger = get_logger("LinuxShorts.ProTabs")

# Type checking için import (runtime'da çalışmaz)
if TYPE_CHECKING:
    from core.preset_manager import VideoPreset

# Modül kontrolleri
try:
    from core.smart_analyzer import SmartVideoAnalyzer, Segment, AnalysisResult
    SMART_ANALYZER_AVAILABLE = True
except ImportError:
    SMART_ANALYZER_AVAILABLE = False

try:
    from core.thumbnail_generator import ThumbnailGenerator, ThumbnailStyle
    from PIL import Image, ImageTk
    THUMBNAIL_AVAILABLE = True
except ImportError:
    THUMBNAIL_AVAILABLE = False

try:
    from core.seo_generator import SEOGenerator, SEOSuggestion
    SEO_AVAILABLE = True
except ImportError:
    SEO_AVAILABLE = False

try:
    from core.preset_manager import PresetManager, VideoPreset
    PRESET_AVAILABLE = True
except ImportError:
    PRESET_AVAILABLE = False


class SmartAnalyzerTab:
    """Akıllı Video Analiz Sekmesi"""
    
    def __init__(self, parent: ctk.CTkFrame, on_segment_select: Optional[Callable] = None):
        self.parent = parent
        self.on_segment_select = on_segment_select
        self.analyzer = SmartVideoAnalyzer() if SMART_ANALYZER_AVAILABLE else None
        self.video_path: Optional[Path] = None
        self.result: Optional[AnalysisResult] = None
        
        self._create_ui()
    
    def _create_ui(self):
        if not SMART_ANALYZER_AVAILABLE:
            self._show_unavailable("Akıllı Analiz modülü yüklenemedi")
            return
        
        # Ana scroll frame
        self.scroll = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Başlık
        header = ctk.CTkFrame(self.scroll, fg_color=("gray92", "gray14"), corner_radius=10)
        header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            header, text="🧠 Akıllı Video Analizi",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=15, padx=15, anchor="w")
        
        ctk.CTkLabel(
            header, text="Sessizlik algılama, hook tespiti, sahne değişiklikleri ve en iyi kesit önerileri",
            font=ctk.CTkFont(size=11), text_color="gray"
        ).pack(pady=(0, 15), padx=15, anchor="w")
        
        # Analiz butonu
        self.analyze_btn = ctk.CTkButton(
            self.scroll, text="🔍 Analizi Başlat", command=self._start_analysis,
            height=40, font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#9b59b6", hover_color="#8e44ad"
        )
        self.analyze_btn.pack(fill="x", pady=(0, 10))
        
        # Progress
        self.progress_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.progress_frame.pack(fill="x", pady=(0, 10))
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame, text="", font=ctk.CTkFont(size=11), text_color="gray"
        )
        self.progress_label.pack(pady=5)
        
        # Sonuçlar
        self.results_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.results_frame.pack(fill="both", expand=True)
    
    def _show_unavailable(self, message: str):
        frame = ctk.CTkFrame(self.parent)
        frame.pack(expand=True, pady=50)
        ctk.CTkLabel(frame, text="⚠️ " + message, font=ctk.CTkFont(size=14), text_color="orange").pack(pady=20, padx=30)
    
    def load_video(self, video_path: Path) -> bool:
        if not self.analyzer:
            return False
        self.video_path = video_path
        return self.analyzer.load_video(video_path)
    
    def _start_analysis(self):
        if not self.video_path or not self.analyzer:
            messagebox.showwarning("Uyarı", "Önce bir video yükleyin!")
            return
        
        self.analyze_btn.configure(state="disabled", text="⏳ Analiz ediliyor...")
        
        def worker():
            def progress(pct, msg):
                self.parent.after(0, lambda: self._update_progress(pct, msg))
            
            result = self.analyzer.full_analysis(progress_callback=progress)
            self.parent.after(0, lambda: self._show_results(result))
        
        threading.Thread(target=worker, daemon=True).start()
    
    def _update_progress(self, percent: int, message: str):
        self.progress_bar.set(percent / 100)
        self.progress_label.configure(text=message)
    
    def _show_results(self, result: AnalysisResult):
        self.result = result
        self.analyze_btn.configure(state="normal", text="🔍 Analizi Başlat")
        
        # Sonuçları temizle
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Özet
        summary = ctk.CTkFrame(self.results_frame, fg_color=("gray92", "gray14"), corner_radius=10)
        summary.pack(fill="x", pady=(10, 5))
        
        ctk.CTkLabel(summary, text="📊 Analiz Özeti", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10, padx=15, anchor="w")
        
        stats = f"• Sessizlik: {len(result.silence_segments)} bölüm\n"
        stats += f"• Konuşma: {len(result.speech_segments)} bölüm\n"
        stats += f"• Sahne değişikliği: {len(result.scene_changes)}\n"
        stats += f"• Hook adayları: {len(result.hook_candidates)}\n"
        stats += f"• Önerilen kesitler: {len(result.best_segments)}"
        
        ctk.CTkLabel(summary, text=stats, font=ctk.CTkFont(size=12), justify="left").pack(pady=(0, 10), padx=15, anchor="w")
        
        # Hook'lar
        if result.hook_candidates:
            self._create_segment_section("🎯 Hook Adayları", result.hook_candidates, "İlk 15 saniyedeki dikkat çekici anlar")
        
        # En iyi kesitler
        if result.best_segments:
            self._create_segment_section("⭐ Önerilen Kesitler", result.best_segments, "En yüksek skorlu Short adayları")
        
        # Sahne değişiklikleri
        if result.scene_changes:
            scene_frame = ctk.CTkFrame(self.results_frame, fg_color=("gray92", "gray14"), corner_radius=10)
            scene_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(scene_frame, text="🎬 Sahne Değişiklikleri", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=10, padx=15, anchor="w")
            
            times = ", ".join([f"{t:.1f}s" for t in result.scene_changes[:10]])
            if len(result.scene_changes) > 10:
                times += f" (+{len(result.scene_changes) - 10} daha)"
            
            ctk.CTkLabel(scene_frame, text=times, font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(0, 10), padx=15, anchor="w")
    
    def _create_segment_section(self, title: str, segments: List[Segment], description: str):
        frame = ctk.CTkFrame(self.results_frame, fg_color=("gray92", "gray14"), corner_radius=10)
        frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=13, weight="bold")).pack(pady=10, padx=15, anchor="w")
        ctk.CTkLabel(frame, text=description, font=ctk.CTkFont(size=10), text_color="gray").pack(pady=(0, 5), padx=15, anchor="w")
        
        for seg in segments[:5]:
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=2)
            
            text = f"⏱️ {self._format_time(seg.start)} → {self._format_time(seg.end)} | {seg.label}"
            ctk.CTkLabel(row, text=text, font=ctk.CTkFont(size=11), anchor="w").pack(side="left", fill="x", expand=True)
            
            ctk.CTkButton(
                row, text="Seç", width=50, height=24,
                command=lambda s=seg: self._select_segment(s),
                font=ctk.CTkFont(size=10)
            ).pack(side="right")
        
        ctk.CTkLabel(frame, text="").pack(pady=5)  # Spacer
    
    def _select_segment(self, segment: Segment):
        if self.on_segment_select:
            self.on_segment_select(segment.start, segment.duration)
        messagebox.showinfo("Seçildi", f"Kesit seçildi: {self._format_time(segment.start)} - {self._format_time(segment.end)}")
    
    def _format_time(self, seconds: float) -> str:
        return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}"


class ThumbnailTab:
    """Thumbnail Oluşturma Sekmesi"""
    
    def __init__(self, parent: ctk.CTkFrame):
        self.parent = parent
        self.generator = ThumbnailGenerator() if THUMBNAIL_AVAILABLE else None
        self.video_path: Optional[Path] = None
        self.preview_image = None
        self.current_style = ThumbnailStyle() if THUMBNAIL_AVAILABLE else None
        
        self._create_ui()
    
    def _create_ui(self):
        if not THUMBNAIL_AVAILABLE:
            self._show_unavailable("Thumbnail modülü yüklenemedi (PIL/OpenCV gerekli)")
            return
        
        self.scroll = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 2 sütun layout
        self.scroll.grid_columnconfigure(0, weight=1)
        self.scroll.grid_columnconfigure(1, weight=1)
        
        # Sol - Önizleme
        preview_frame = ctk.CTkFrame(self.scroll, fg_color=("gray92", "gray14"), corner_radius=10)
        preview_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
        
        ctk.CTkLabel(preview_frame, text="🖼️ Önizleme", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        self.preview_canvas = ctk.CTkLabel(preview_frame, text="", width=320, height=180, fg_color="gray20")
        self.preview_canvas.pack(pady=10, padx=10)
        
        # Zaman seçici
        time_frame = ctk.CTkFrame(preview_frame, fg_color="transparent")
        time_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(time_frame, text="Zaman:", font=ctk.CTkFont(size=11)).pack(side="left")
        self.time_slider = ctk.CTkSlider(time_frame, from_=0, to=100, command=self._on_time_change)
        self.time_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.time_label = ctk.CTkLabel(time_frame, text="00:00", font=ctk.CTkFont(size=11))
        self.time_label.pack(side="right")
        
        # En iyi frame'leri bul
        ctk.CTkButton(
            preview_frame, text="🔍 En İyi Frame'leri Bul", command=self._find_best_frames,
            height=32, font=ctk.CTkFont(size=12)
        ).pack(fill="x", padx=10, pady=10)
        
        # Frame adayları
        self.candidates_frame = ctk.CTkFrame(preview_frame, fg_color="transparent")
        self.candidates_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Sağ - Ayarlar
        settings_frame = ctk.CTkFrame(self.scroll, fg_color=("gray92", "gray14"), corner_radius=10)
        settings_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
        
        ctk.CTkLabel(settings_frame, text="⚙️ Ayarlar", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        # Başlık
        ctk.CTkLabel(settings_frame, text="Başlık Metni:", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=10)
        self.title_entry = ctk.CTkEntry(settings_frame, placeholder_text="Thumbnail başlığı...")
        self.title_entry.pack(fill="x", padx=10, pady=5)
        
        # Efektler
        effects_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        effects_frame.pack(fill="x", padx=10, pady=10)
        
        self.vignette_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(effects_frame, text="Vignette", variable=self.vignette_var, command=self._update_preview).pack(side="left")
        
        # Parlaklık
        bright_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        bright_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(bright_frame, text="Parlaklık:", font=ctk.CTkFont(size=11)).pack(side="left")
        self.brightness_slider = ctk.CTkSlider(bright_frame, from_=0.5, to=1.5, command=self._on_style_change)
        self.brightness_slider.set(1.1)
        self.brightness_slider.pack(side="right", fill="x", expand=True, padx=10)
        
        # Kontrast
        contrast_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        contrast_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(contrast_frame, text="Kontrast:", font=ctk.CTkFont(size=11)).pack(side="left")
        self.contrast_slider = ctk.CTkSlider(contrast_frame, from_=0.5, to=1.5, command=self._on_style_change)
        self.contrast_slider.set(1.2)
        self.contrast_slider.pack(side="right", fill="x", expand=True, padx=10)
        
        # Doygunluk
        sat_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        sat_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(sat_frame, text="Doygunluk:", font=ctk.CTkFont(size=11)).pack(side="left")
        self.saturation_slider = ctk.CTkSlider(sat_frame, from_=0.5, to=2.0, command=self._on_style_change)
        self.saturation_slider.set(1.3)
        self.saturation_slider.pack(side="right", fill="x", expand=True, padx=10)
        
        # Kaydet butonları
        btn_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=15)
        
        ctk.CTkButton(
            btn_frame, text="💾 Kaydet", command=self._save_thumbnail,
            fg_color="#27ae60", hover_color="#229954"
        ).pack(side="left", expand=True, padx=2)
        
        ctk.CTkButton(
            btn_frame, text="📁 5 Adet Kaydet", command=self._save_multiple,
            fg_color="#3498db", hover_color="#2980b9"
        ).pack(side="left", expand=True, padx=2)
    
    def _show_unavailable(self, message: str):
        frame = ctk.CTkFrame(self.parent)
        frame.pack(expand=True, pady=50)
        ctk.CTkLabel(frame, text="⚠️ " + message, font=ctk.CTkFont(size=14), text_color="orange").pack(pady=20, padx=30)
    
    def load_video(self, video_path: Path) -> bool:
        if not self.generator:
            return False
        self.video_path = video_path
        if self.generator.load_video(video_path):
            self.time_slider.configure(to=self.generator.duration)
            self._update_preview()
            return True
        return False
    
    def _on_time_change(self, value):
        self.time_label.configure(text=f"{int(value // 60):02d}:{int(value % 60):02d}")
        self._update_preview()
    
    def _on_style_change(self, value=None):
        self._update_preview()
    
    def _update_preview(self):
        if not self.generator or not self.video_path:
            return
        
        try:
            style = ThumbnailStyle(
                title_text=self.title_entry.get(),
                brightness=self.brightness_slider.get(),
                contrast=self.contrast_slider.get(),
                saturation=self.saturation_slider.get(),
                vignette=self.vignette_var.get()
            )
            
            preview = self.generator.get_preview(self.time_slider.get(), style, (320, 180))
            if preview:
                self.preview_image = ImageTk.PhotoImage(preview)
                self.preview_canvas.configure(image=self.preview_image, text="")
        except Exception as e:
            logger.error(f"Preview hatası: {e}")
    
    def _find_best_frames(self):
        if not self.generator or not self.video_path:
            messagebox.showwarning("Uyarı", "Önce video yükleyin!")
            return
        
        candidates = self.generator.find_best_frames(5)
        
        for w in self.candidates_frame.winfo_children():
            w.destroy()
        
        if candidates:
            ctk.CTkLabel(self.candidates_frame, text="En iyi frame'ler:", font=ctk.CTkFont(size=10)).pack(anchor="w")
            for c in candidates:
                btn = ctk.CTkButton(
                    self.candidates_frame, 
                    text=f"{int(c.time // 60):02d}:{int(c.time % 60):02d} ({c.reason})",
                    command=lambda t=c.time: self._select_frame(t),
                    height=24, font=ctk.CTkFont(size=10)
                )
                btn.pack(fill="x", pady=1)
    
    def _select_frame(self, time: float):
        self.time_slider.set(time)
        self._on_time_change(time)
    
    def _save_thumbnail(self):
        if not self.generator or not self.video_path:
            return
        
        style = ThumbnailStyle(
            title_text=self.title_entry.get(),
            brightness=self.brightness_slider.get(),
            contrast=self.contrast_slider.get(),
            saturation=self.saturation_slider.get(),
            vignette=self.vignette_var.get()
        )
        
        path = self.generator.generate_thumbnail(self.time_slider.get(), style)
        if path:
            messagebox.showinfo("Başarılı", f"Thumbnail kaydedildi:\n{path}")
    
    def _save_multiple(self):
        if not self.generator or not self.video_path:
            return
        
        paths = self.generator.generate_multiple(5)
        if paths:
            messagebox.showinfo("Başarılı", f"{len(paths)} thumbnail kaydedildi!")


class SEOTab:
    """SEO Önerileri Sekmesi"""
    
    def __init__(self, parent: ctk.CTkFrame):
        self.parent = parent
        self.generator = SEOGenerator() if SEO_AVAILABLE else None
        self.transcript: str = ""
        
        self._create_ui()
    
    def _create_ui(self):
        if not SEO_AVAILABLE:
            self._show_unavailable("SEO modülü yüklenemedi")
            return
        
        self.scroll = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Başlık
        header = ctk.CTkFrame(self.scroll, fg_color=("gray92", "gray14"), corner_radius=10)
        header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header, text="📊 YouTube SEO Önerileri", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15, padx=15, anchor="w")
        ctk.CTkLabel(header, text="Başlık, açıklama ve hashtag önerileri", font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(0, 15), padx=15, anchor="w")
        
        # Konu girişi
        topic_frame = ctk.CTkFrame(self.scroll, fg_color=("gray92", "gray14"), corner_radius=10)
        topic_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(topic_frame, text="Video Konusu:", font=ctk.CTkFont(size=12)).pack(pady=10, padx=15, anchor="w")
        
        self.topic_entry = ctk.CTkEntry(topic_frame, placeholder_text="Örn: Linux Terminal, Python Eğitimi...")
        self.topic_entry.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkButton(
            topic_frame, text="✨ Öneriler Oluştur", command=self._generate_suggestions,
            height=35, font=ctk.CTkFont(size=13)
        ).pack(fill="x", padx=15, pady=(0, 15))
        
        # Sonuçlar
        self.results_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.results_frame.pack(fill="both", expand=True, pady=10)
        
        # İpuçları
        tips_frame = ctk.CTkFrame(self.scroll, fg_color=("gray88", "gray20"), corner_radius=10)
        tips_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(tips_frame, text="💡 SEO İpuçları", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=10, padx=15, anchor="w")
        
        tips = self.generator.get_optimization_tips() if self.generator else []
        for tip in tips[:5]:
            ctk.CTkLabel(tips_frame, text=tip, font=ctk.CTkFont(size=10), text_color="gray").pack(pady=2, padx=15, anchor="w")
        
        ctk.CTkLabel(tips_frame, text="").pack(pady=5)
    
    def _show_unavailable(self, message: str):
        frame = ctk.CTkFrame(self.parent)
        frame.pack(expand=True, pady=50)
        ctk.CTkLabel(frame, text="⚠️ " + message, font=ctk.CTkFont(size=14), text_color="orange").pack(pady=20, padx=30)
    
    def set_transcript(self, transcript: str):
        self.transcript = transcript
        if self.generator:
            self.generator.analyze_content(transcript)
    
    def _generate_suggestions(self):
        if not self.generator:
            return
        
        topic = self.topic_entry.get().strip()
        if not topic and not self.transcript:
            messagebox.showwarning("Uyarı", "Bir konu girin veya altyazı oluşturun!")
            return
        
        self.generator.analyze_content(self.transcript, topic)
        suggestions = self.generator.generate_multiple_suggestions(3)
        
        # Sonuçları temizle
        for w in self.results_frame.winfo_children():
            w.destroy()
        
        for i, sug in enumerate(suggestions):
            frame = ctk.CTkFrame(self.results_frame, fg_color=("gray92", "gray14"), corner_radius=10)
            frame.pack(fill="x", pady=5)
            
            # Başlık
            title_frame = ctk.CTkFrame(frame, fg_color="transparent")
            title_frame.pack(fill="x", padx=15, pady=10)
            
            ctk.CTkLabel(title_frame, text=f"Öneri #{i+1}", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
            ctk.CTkLabel(title_frame, text=f"Skor: {sug.score:.0f}/100", font=ctk.CTkFont(size=11), text_color="gray").pack(side="right")
            
            # Başlık önerisi
            ctk.CTkLabel(frame, text="📌 Başlık:", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=15)
            
            title_entry = ctk.CTkEntry(frame, height=30)
            title_entry.insert(0, sug.title)
            title_entry.pack(fill="x", padx=15, pady=5)
            
            # Hashtag'ler
            ctk.CTkLabel(frame, text="🏷️ Hashtag'ler:", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=15, pady=(10, 0))
            
            hashtag_text = " ".join(sug.hashtags[:10])
            ctk.CTkLabel(frame, text=hashtag_text, font=ctk.CTkFont(size=10), text_color="#3498db", wraplength=350).pack(anchor="w", padx=15, pady=5)
            
            # Kopyala butonu
            ctk.CTkButton(
                frame, text="📋 Kopyala", height=28,
                command=lambda t=sug.title, h=hashtag_text: self._copy_to_clipboard(t, h)
            ).pack(anchor="e", padx=15, pady=10)
    
    def _copy_to_clipboard(self, title: str, hashtags: str):
        text = f"{title}\n\n{hashtags}"
        self.parent.clipboard_clear()
        self.parent.clipboard_append(text)
        messagebox.showinfo("Kopyalandı", "Başlık ve hashtag'ler panoya kopyalandı!")


class PresetTab:
    """Preset Yönetimi Sekmesi"""
    
    def __init__(self, parent: ctk.CTkFrame, on_preset_apply: Optional[Callable] = None):
        self.parent = parent
        self.on_preset_apply = on_preset_apply
        self.manager = PresetManager() if PRESET_AVAILABLE else None
        
        self._create_ui()
    
    def _create_ui(self):
        if not PRESET_AVAILABLE:
            self._show_unavailable("Preset modülü yüklenemedi")
            return
        
        self.scroll = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Başlık
        header = ctk.CTkFrame(self.scroll, fg_color=("gray92", "gray14"), corner_radius=10)
        header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header, text="🎛️ Preset Yönetimi", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15, padx=15, anchor="w")
        ctk.CTkLabel(header, text="Ayarlarınızı kaydedin ve tekrar kullanın", font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(0, 15), padx=15, anchor="w")
        
        # Preset listesi
        self.presets_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.presets_frame.pack(fill="both", expand=True)
        
        self._refresh_presets()
        
        # Yeni preset oluştur
        new_frame = ctk.CTkFrame(self.scroll, fg_color=("gray92", "gray14"), corner_radius=10)
        new_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(new_frame, text="➕ Yeni Preset", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=10, padx=15, anchor="w")
        
        self.new_name_entry = ctk.CTkEntry(new_frame, placeholder_text="Preset adı...")
        self.new_name_entry.pack(fill="x", padx=15, pady=5)
        
        self.new_desc_entry = ctk.CTkEntry(new_frame, placeholder_text="Açıklama (opsiyonel)")
        self.new_desc_entry.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkButton(
            new_frame, text="💾 Mevcut Ayarları Kaydet", command=self._save_current,
            height=35, fg_color="#27ae60", hover_color="#229954"
        ).pack(fill="x", padx=15, pady=15)
    
    def _show_unavailable(self, message: str):
        frame = ctk.CTkFrame(self.parent)
        frame.pack(expand=True, pady=50)
        ctk.CTkLabel(frame, text="⚠️ " + message, font=ctk.CTkFont(size=14), text_color="orange").pack(pady=20, padx=30)
    
    def _refresh_presets(self):
        for w in self.presets_frame.winfo_children():
            w.destroy()
        
        if not self.manager:
            return
        
        presets = self.manager.get_all_presets()
        
        for preset in presets:
            frame = ctk.CTkFrame(self.presets_frame, fg_color=("gray92", "gray14"), corner_radius=8)
            frame.pack(fill="x", pady=3)
            
            # Sol - bilgi
            info = ctk.CTkFrame(frame, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=10, pady=8)
            
            ctk.CTkLabel(info, text=preset.name, font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
            
            if preset.description:
                ctk.CTkLabel(info, text=preset.description, font=ctk.CTkFont(size=10), text_color="gray").pack(anchor="w")
            
            details = f"Zoom: {preset.scale:.0f}% | BG: {preset.bg_mode} | CRF: {preset.crf}"
            ctk.CTkLabel(info, text=details, font=ctk.CTkFont(size=9), text_color="gray").pack(anchor="w")
            
            # Sağ - butonlar
            btns = ctk.CTkFrame(frame, fg_color="transparent")
            btns.pack(side="right", padx=10, pady=8)
            
            ctk.CTkButton(
                btns, text="Uygula", width=60, height=26,
                command=lambda p=preset: self._apply_preset(p)
            ).pack(side="left", padx=2)
            
            # Varsayılan presetler silinemez
            is_default = any(p.name == preset.name for p in self.manager.presets.values())
            if preset.category != "genel":
                ctk.CTkButton(
                    btns, text="🗑️", width=30, height=26,
                    command=lambda p=preset: self._delete_preset(p),
                    fg_color="#e74c3c", hover_color="#c0392b"
                ).pack(side="left", padx=2)
    
    def _apply_preset(self, preset: VideoPreset):
        if self.on_preset_apply:
            self.on_preset_apply(preset)
        messagebox.showinfo("Uygulandı", f"'{preset.name}' preset'i uygulandı!")
    
    def _delete_preset(self, preset: VideoPreset):
        if messagebox.askyesno("Sil", f"'{preset.name}' preset'ini silmek istediğinize emin misiniz?"):
            self.manager.delete_preset(preset.name)
            self._refresh_presets()
    
    def _save_current(self):
        name = self.new_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Uyarı", "Preset adı girin!")
            return
        
        desc = self.new_desc_entry.get().strip()
        
        preset = VideoPreset(name=name, description=desc, category="kullanıcı")
        
        if self.manager.save_preset(preset):
            messagebox.showinfo("Başarılı", f"'{name}' preset'i kaydedildi!")
            self.new_name_entry.delete(0, "end")
            self.new_desc_entry.delete(0, "end")
            self._refresh_presets()
        else:
            messagebox.showerror("Hata", "Preset kaydedilemedi!")
