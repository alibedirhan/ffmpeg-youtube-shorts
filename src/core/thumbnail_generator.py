"""
LinuxShorts Pro - Thumbnail Generator
Otomatik ve özelleştirilebilir thumbnail oluşturma
"""

from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Tuple
import numpy as np

from utils.logger import get_logger

logger = get_logger("LinuxShorts.Thumbnail")

try:
    import cv2
    from PIL import Image, ImageDraw, ImageFont, ImageEnhance
    IMAGING_AVAILABLE = True
except ImportError:
    IMAGING_AVAILABLE = False
    logger.warning("OpenCV veya PIL bulunamadı")


@dataclass
class ThumbnailStyle:
    """Thumbnail stil ayarları"""
    width: int = 1280
    height: int = 720
    title_text: str = ""
    title_font_size: int = 72
    title_color: str = "#FFFFFF"
    title_stroke_color: str = "#000000"
    title_stroke_width: int = 4
    title_position: str = "center"
    brightness: float = 1.1
    contrast: float = 1.2
    saturation: float = 1.3
    vignette: bool = True
    overlay_color: str = ""
    overlay_opacity: float = 0.3
    border_width: int = 0
    border_color: str = "#FF0000"


@dataclass
class FrameCandidate:
    """Thumbnail adayı frame"""
    time: float
    score: float
    image: Optional[np.ndarray] = None
    reason: str = ""


class ThumbnailGenerator:
    """Thumbnail oluşturucu"""
    
    def __init__(self):
        self.video_path: Optional[Path] = None
        self.duration: float = 0.0
        self.fps: float = 30.0
        self.width: int = 0
        self.height: int = 0
        self.candidates: List[FrameCandidate] = []
    
    def load_video(self, video_path: Path) -> bool:
        """Video yükle"""
        if not IMAGING_AVAILABLE:
            return False
        
        self.video_path = Path(video_path)
        if not self.video_path.exists():
            return False
        
        try:
            cap = cv2.VideoCapture(str(self.video_path))
            if not cap.isOpened():
                return False
            
            self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.fps = cap.get(cv2.CAP_PROP_FPS)
            self.duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / self.fps
            cap.release()
            return True
        except:
            return False
    
    def get_frame_at(self, time_sec: float) -> Optional[np.ndarray]:
        """Belirli zamandaki frame'i al"""
        if not IMAGING_AVAILABLE or not self.video_path:
            return None
        
        try:
            cap = cv2.VideoCapture(str(self.video_path))
            frame_num = int(time_sec * self.fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            cap.release()
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) if ret else None
        except:
            return None
    
    def calculate_frame_score(self, frame: np.ndarray) -> Tuple[float, str]:
        """Frame kalitesini değerlendir"""
        score = 50.0
        reasons = []
        
        brightness = np.mean(frame)
        if 80 < brightness < 180:
            score += 15
            reasons.append("İyi parlaklık")
        
        contrast = np.std(frame)
        if contrast > 50:
            score += 15
            reasons.append("Yüksek kontrast")
        
        if len(frame.shape) == 3:
            hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
            if np.mean(hsv[:, :, 1]) > 80:
                score += 10
                reasons.append("Renkli")
        
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        if cv2.Laplacian(gray, cv2.CV_64F).var() > 100:
            score += 15
            reasons.append("Keskin")
        
        try:
            cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = cascade.detectMultiScale(gray, 1.1, 4)
            if len(faces) > 0:
                score += 20
                reasons.append(f"{len(faces)} yüz")
        except:
            pass
        
        return score, ", ".join(reasons) if reasons else "Normal"
    
    def find_best_frames(self, num_candidates: int = 10, sample_interval: float = 2.0) -> List[FrameCandidate]:
        """En iyi frame'leri bul"""
        if not IMAGING_AVAILABLE or not self.video_path:
            return []
        
        candidates = []
        try:
            cap = cv2.VideoCapture(str(self.video_path))
            frame_interval = max(1, int(self.fps * sample_interval))
            frame_idx = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % frame_interval == 0:
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    score, reason = self.calculate_frame_score(rgb)
                    candidates.append(FrameCandidate(
                        time=frame_idx / self.fps,
                        score=score, image=rgb, reason=reason
                    ))
                frame_idx += 1
            
            cap.release()
            candidates.sort(key=lambda x: x.score, reverse=True)
            self.candidates = candidates[:num_candidates]
            return self.candidates
        except:
            return []
    
    def apply_style(self, image: np.ndarray, style: ThumbnailStyle) -> Image.Image:
        """Stil uygula"""
        pil = Image.fromarray(image).resize((style.width, style.height), Image.LANCZOS)
        
        if style.brightness != 1.0:
            pil = ImageEnhance.Brightness(pil).enhance(style.brightness)
        if style.contrast != 1.0:
            pil = ImageEnhance.Contrast(pil).enhance(style.contrast)
        if style.saturation != 1.0:
            pil = ImageEnhance.Color(pil).enhance(style.saturation)
        
        if style.overlay_color:
            overlay = Image.new('RGBA', pil.size, style.overlay_color)
            overlay.putalpha(int(255 * style.overlay_opacity))
            pil = Image.alpha_composite(pil.convert('RGBA'), overlay).convert('RGB')
        
        if style.vignette:
            pil = self._apply_vignette(pil)
        
        if style.title_text:
            pil = self._add_text(pil, style)
        
        return pil
    
    def _apply_vignette(self, image: Image.Image) -> Image.Image:
        """Vignette efekti"""
        w, h = image.size
        x, y = np.meshgrid(np.linspace(-1, 1, w), np.linspace(-1, 1, h))
        vignette = 1 - np.clip(np.sqrt(x**2 + y**2) * 0.7, 0, 1) * 0.5
        arr = np.array(image).astype(float)
        for i in range(3):
            arr[:, :, i] *= vignette
        return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    
    def _add_text(self, image: Image.Image, style: ThumbnailStyle) -> Image.Image:
        """Metin ekle"""
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", style.title_font_size)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), style.title_text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (image.width - tw) // 2
        
        if style.title_position == "top":
            y = 50
        elif style.title_position == "bottom":
            y = image.height - th - 80
        else:
            y = (image.height - th) // 2
        
        # Stroke
        for dx in range(-style.title_stroke_width, style.title_stroke_width + 1):
            for dy in range(-style.title_stroke_width, style.title_stroke_width + 1):
                draw.text((x + dx, y + dy), style.title_text, font=font, fill=style.title_stroke_color)
        
        draw.text((x, y), style.title_text, font=font, fill=style.title_color)
        return image
    
    def generate_thumbnail(self, time_sec: float = None, style: ThumbnailStyle = None,
                          output_path: Path = None) -> Optional[Path]:
        """Thumbnail oluştur"""
        if style is None:
            style = ThumbnailStyle()
        
        if time_sec is None:
            if not self.candidates:
                self.find_best_frames(5)
            frame = self.candidates[0].image if self.candidates else self.get_frame_at(self.duration * 0.25)
        else:
            frame = self.get_frame_at(time_sec)
        
        if frame is None:
            return None
        
        thumbnail = self.apply_style(frame, style)
        
        if output_path is None:
            output_path = self.video_path.parent / f"{self.video_path.stem}_thumbnail.jpg"
        
        thumbnail.save(str(output_path), "JPEG", quality=95)
        return Path(output_path)
    
    def generate_multiple(self, count: int = 5, style: ThumbnailStyle = None,
                         output_dir: Path = None) -> List[Path]:
        """Birden fazla thumbnail"""
        if not self.candidates:
            self.find_best_frames(count)
        
        if output_dir is None:
            output_dir = self.video_path.parent / "thumbnails"
        
        Path(output_dir).mkdir(exist_ok=True)
        
        results = []
        for i, c in enumerate(self.candidates[:count]):
            path = Path(output_dir) / f"thumb_{i+1}_{c.time:.1f}s.jpg"
            if style is None:
                style = ThumbnailStyle()
            self.apply_style(c.image, style).save(str(path), "JPEG", quality=95)
            results.append(path)
        
        return results
