"""
LinuxShorts Generator - Professional Video Editor Core
YouTube Shorts için profesyonel video düzenleme motoru
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Callable, List
from dataclasses import dataclass, field
from PIL import Image, ImageDraw, ImageFilter
import subprocess

from utils.logger import get_logger

logger = get_logger("LinuxShorts.VideoEditor")


@dataclass
class VideoTransform:
    """Video dönüşüm ayarları - Hassas kontrol"""
    # Scale (%)
    # 100 = orijinal genişlik, >100 = zoom (kırpma), <100 = küçültme
    scale: float = 100.0  # 30-300% önerilen aralık
    
    # Pozisyon (piksel offset, merkez = 0,0)
    pos_x: int = 0  # -500 to +500
    pos_y: int = 0  # -500 to +500
    
    # Arka plan
    bg_mode: str = "blur"  # black, blur, gradient, color, image
    bg_color: str = "000000"
    bg_blur_strength: int = 25
    bg_gradient_start: str = "1a1a2e"
    bg_gradient_end: str = "16213e"
    
    # Output ayarları
    output_width: int = 1080
    output_height: int = 1920
    
    # Kalite ayarları
    crf: int = 23  # 18-28 (düşük = yüksek kalite)
    preset: str = "medium"  # ultrafast, fast, medium, slow
    fps: Optional[float] = None  # None = orijinal FPS


@dataclass 
class SafeZone:
    """YouTube güvenli alan tanımları"""
    # YouTube Shorts'ta UI elementlerinin kaplayabileceği alanlar
    top_margin: int = 120  # Üstte profil, başlık
    bottom_margin: int = 180  # Altta like, comment, share
    side_margin: int = 50  # Yanlarda


class VideoFrameReader:
    """Video frame okuyucu (OpenCV tabanlı)"""
    
    def __init__(self, video_path: Path):
        self.video_path = video_path
        self.cap: Optional[cv2.VideoCapture] = None
        self.total_frames = 0
        self.fps = 0.0
        self.width = 0
        self.height = 0
        self.duration = 0.0
        self._open()
    
    def _open(self):
        """Video dosyasını aç"""
        self.cap = cv2.VideoCapture(str(self.video_path))
        if not self.cap.isOpened():
            raise RuntimeError(f"Video açılamadı: {self.video_path}")
        
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.duration = self.total_frames / self.fps if self.fps > 0 else 0
        
        logger.info(f"Video açıldı: {self.width}x{self.height}, {self.duration:.1f}s, {self.fps:.1f}fps")
    
    def get_frame(self, time_seconds: float) -> Optional[np.ndarray]:
        """Belirli zamandaki frame'i al"""
        if self.cap is None:
            return None
        
        frame_number = int(time_seconds * self.fps)
        frame_number = max(0, min(frame_number, self.total_frames - 1))
        
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.cap.read()
        
        return frame if ret else None
    
    def get_frame_as_pil(self, time_seconds: float) -> Optional[Image.Image]:
        """Frame'i PIL Image olarak al (RGB)"""
        frame = self.get_frame(time_seconds)
        if frame is not None:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return Image.fromarray(rgb_frame)
        return None
    
    def get_thumbnails(self, count: int = 10) -> List[Image.Image]:
        """Timeline için thumbnail'ler oluştur"""
        thumbnails = []
        interval = self.duration / count
        
        for i in range(count):
            time_sec = i * interval
            frame = self.get_frame_as_pil(time_sec)
            if frame:
                # Küçük thumbnail
                thumb = frame.resize((80, 45), Image.Resampling.LANCZOS)
                thumbnails.append(thumb)
        
        return thumbnails
    
    def close(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
    
    def __del__(self):
        self.close()


class ProVideoEditor:
    """
    Profesyonel Video Editor
    Hassas kontrol ve gelişmiş özellikler
    """
    
    def __init__(self):
        self.frame_reader: Optional[VideoFrameReader] = None
        self.transform = VideoTransform()
        self.safe_zone = SafeZone()
        self.current_frame: Optional[Image.Image] = None
        self.current_time: float = 0.0
        
        # Önizleme ayarları
        self.preview_width = 360
        self.preview_height = 640
        
        # UI ayarları
        self.show_safe_zone = True
        self.show_grid = False
        self.show_center_lines = True
        
        logger.info("ProVideoEditor başlatıldı")
    
    def load_video(self, video_path: Path) -> bool:
        """Video yükle"""
        try:
            if self.frame_reader:
                self.frame_reader.close()
            
            self.frame_reader = VideoFrameReader(video_path)
            self.transform = VideoTransform()
            self.current_time = 0.0
            
            # İlk frame'i al
            self.update_frame(0.0)
            
            logger.info(f"Video yüklendi: {video_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Video yükleme hatası: {e}")
            return False
    
    def update_frame(self, time_seconds: float) -> Optional[Image.Image]:
        """Frame güncelle"""
        if self.frame_reader is None:
            return None
        
        self.current_time = max(0, min(time_seconds, self.frame_reader.duration))
        self.current_frame = self.frame_reader.get_frame_as_pil(self.current_time)
        return self.current_frame
    
    def get_preview_image(self) -> Optional[Image.Image]:
        """
        Önizleme görüntüsü oluştur
        16:9 video → 9:16 önizleme
        """
        if self.current_frame is None or self.frame_reader is None:
            return None
        
        frame = self.current_frame
        vw, vh = frame.size  # Video boyutları (1920x1080)
        pw, ph = self.preview_width, self.preview_height  # Preview boyutları (360x640)
        
        video_ratio = vw / vh  # 16:9 = 1.777
        
        # 1. Arka plan oluştur
        preview = self._create_background(frame, pw, ph)
        
        # 2. Video'yu scale et
        # Video genişliği = preview genişliği * scale faktörü
        scale_factor = self.transform.scale / 100.0
        
        scaled_w = int(pw * scale_factor)
        scaled_h = int(scaled_w / video_ratio)
        
        # Minimum boyut
        scaled_w = max(50, scaled_w)
        scaled_h = max(30, scaled_h)
        
        scaled_frame = frame.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)
        
        # 3. Pozisyon hesapla
        center_x = (pw - scaled_w) // 2
        center_y = (ph - scaled_h) // 2
        
        # User offset'i preview scale'ine çevir
        offset_scale = pw / self.transform.output_width
        pos_x = center_x + int(self.transform.pos_x * offset_scale)
        pos_y = center_y + int(self.transform.pos_y * offset_scale)
        
        # Sınırlar
        # Eğer video preview'den küçükse  -> 0 .. (pw - scaled_w)
        # Eğer video preview'den büyükse  -> (pw - scaled_w) .. 0
        min_x = min(0, pw - scaled_w)
        max_x = max(0, pw - scaled_w)
        min_y = min(0, ph - scaled_h)
        max_y = max(0, ph - scaled_h)

        pos_x = max(min_x, min(max_x, pos_x))
        pos_y = max(min_y, min(max_y, pos_y))
        
        # 4. Video'yu yapıştır
        preview.paste(scaled_frame, (pos_x, pos_y))
        
        # 5. UI Overlay'leri çiz
        preview = self._draw_overlays(preview)
        
        return preview
    
    def _create_background(self, frame: Image.Image, width: int, height: int) -> Image.Image:
        """Arka plan oluştur"""
        mode = self.transform.bg_mode
        
        if mode == "blur":
            # Blur arka plan
            bg = frame.resize((width, height), Image.Resampling.LANCZOS)
            bg = bg.filter(ImageFilter.GaussianBlur(radius=self.transform.bg_blur_strength // 2))
            return bg
        
        elif mode == "gradient":
            # Gradient arka plan
            bg = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(bg)
            
            start = self._hex_to_rgb(self.transform.bg_gradient_start)
            end = self._hex_to_rgb(self.transform.bg_gradient_end)
            
            for y in range(height):
                ratio = y / height
                r = int(start[0] + (end[0] - start[0]) * ratio)
                g = int(start[1] + (end[1] - start[1]) * ratio)
                b = int(start[2] + (end[2] - start[2]) * ratio)
                draw.line([(0, y), (width, y)], fill=(r, g, b))
            
            return bg
        
        elif mode == "color":
            # Düz renk
            color = self._hex_to_rgb(self.transform.bg_color)
            return Image.new('RGB', (width, height), color)
        
        else:  # black
            return Image.new('RGB', (width, height), (0, 0, 0))
    
    def _draw_overlays(self, image: Image.Image) -> Image.Image:
        """UI overlay'lerini çiz"""
        draw = ImageDraw.Draw(image, 'RGBA')
        w, h = image.size
        
        # Güvenli alan göstergesi
        if self.show_safe_zone:
            # Scale safe zone to preview
            scale = h / self.transform.output_height
            top = int(self.safe_zone.top_margin * scale)
            bottom = h - int(self.safe_zone.bottom_margin * scale)
            side = int(self.safe_zone.side_margin * scale)
            
            # Yarı saydam kırmızı alanlar
            overlay_color = (255, 0, 0, 40)
            
            # Üst alan
            draw.rectangle([(0, 0), (w, top)], fill=overlay_color)
            # Alt alan
            draw.rectangle([(0, bottom), (w, h)], fill=overlay_color)
            # Sol alan
            draw.rectangle([(0, top), (side, bottom)], fill=overlay_color)
            # Sağ alan
            draw.rectangle([(w - side, top), (w, bottom)], fill=overlay_color)
            
            # Güvenli alan çerçevesi
            draw.rectangle(
                [(side, top), (w - side, bottom)],
                outline=(0, 255, 0, 100),
                width=1
            )
        
        # Grid çizgileri
        if self.show_grid:
            grid_color = (255, 255, 255, 30)
            # 3x3 grid
            for i in range(1, 3):
                x = w * i // 3
                y = h * i // 3
                draw.line([(x, 0), (x, h)], fill=grid_color, width=1)
                draw.line([(0, y), (w, y)], fill=grid_color, width=1)
        
        # Merkez çizgileri
        if self.show_center_lines:
            center_color = (255, 255, 0, 60)
            cx, cy = w // 2, h // 2
            # Dikey merkez
            draw.line([(cx, 0), (cx, h)], fill=center_color, width=1)
            # Yatay merkez
            draw.line([(0, cy), (w, cy)], fill=center_color, width=1)
            # Merkez nokta
            draw.ellipse([(cx-3, cy-3), (cx+3, cy+3)], fill=(255, 255, 0, 100))
        
        return image
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Hex rengi RGB'ye çevir"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # ========================================
    # TRANSFORM METODLARI
    # ========================================
    
    def set_scale(self, scale: float):
        """Scale ayarla (%30-300)
        100 = orijinal genişlik, >100 = zoom (kırpma), <100 = küçültme
        """
        # Güvenli aralık: 30–300
        self.transform.scale = max(30.0, min(300.0, float(scale)))
    
    def set_position(self, x: int, y: int):
        """Pozisyon ayarla (piksel)"""
        self.transform.pos_x = max(-500, min(500, x))
        self.transform.pos_y = max(-500, min(500, y))
    
    def set_background_mode(self, mode: str):
        """Arka plan modu"""
        if mode in ["black", "blur", "gradient", "color"]:
            self.transform.bg_mode = mode
    
    def set_background_color(self, hex_color: str):
        """Arka plan rengi"""
        self.transform.bg_color = hex_color.lstrip('#')
    
    def set_blur_strength(self, strength: int):
        """Blur gücü"""
        self.transform.bg_blur_strength = max(5, min(50, strength))
    
    def set_gradient_colors(self, start: str, end: str):
        """Gradient renkleri"""
        self.transform.bg_gradient_start = start.lstrip('#')
        self.transform.bg_gradient_end = end.lstrip('#')
    
    def set_quality(self, crf: int, preset: str):
        """Kalite ayarları"""
        self.transform.crf = max(18, min(28, crf))
        if preset in ["ultrafast", "fast", "medium", "slow", "slower"]:
            self.transform.preset = preset
    
    def center_video(self):
        """Videoyu ortala"""
        self.transform.pos_x = 0
        self.transform.pos_y = 0
    
    def fit_to_width(self):
        """Genişliğe sığdır"""
        if self.frame_reader:
            vw, vh = self.frame_reader.width, self.frame_reader.height
            video_ratio = vw / vh
            target_ratio = 9 / 16
            
            if video_ratio > target_ratio:
                self.transform.scale = 100.0
            else:
                self.transform.scale = (video_ratio / target_ratio) * 100.0
    
    def fit_to_height(self):
        """Yüksekliğe sığdır"""
        if self.frame_reader:
            vw, vh = self.frame_reader.width, self.frame_reader.height
            video_ratio = vw / vh
            target_ratio = 9 / 16
            
            if video_ratio < target_ratio:
                self.transform.scale = 100.0
            else:
                self.transform.scale = (target_ratio / video_ratio) * 100.0
    
    def reset_transform(self):
        """Tüm transform'ları sıfırla"""
        self.transform.scale = 100.0
        self.transform.pos_x = 0
        self.transform.pos_y = 0
    
    # ========================================
    # FFmpeg EXPORT
    # ========================================
    
    def build_ffmpeg_filter(self) -> str:
        """
        FFmpeg filter string oluştur
        
        16:9 yatay video → 9:16 dikey Short
        Video genişliğe sığdırılır, üst/alt boşluk arka plan ile doldurulur
        """
        if self.frame_reader is None:
            return ""
        
        vw, vh = self.frame_reader.width, self.frame_reader.height
        ow, oh = self.transform.output_width, self.transform.output_height  # 1080x1920
        
        # 16:9 videoyu 9:16 çerçeveye sığdırma stratejisi:
        # Video GENİŞLİĞE göre scale edilir (1080px genişlik)
        # Yükseklik orantılı olarak hesaplanır
        # Üst ve alt boşluklar arka plan ile doldurulur
        
        video_ratio = vw / vh  # 16:9 = 1.777
        
        # Scale faktörü (%30-300)
        scale_factor = self.transform.scale / 100.0
        
        # Video genişliği = output genişliği * scale
        final_w = int(ow * scale_factor)
        # Video yüksekliği = genişlik / video oranı
        final_h = int(final_w / video_ratio)
        
        # Çift sayı yap (FFmpeg gereksinimi)
        final_w = final_w - (final_w % 2)
        final_h = final_h - (final_h % 2)
        
        # Minimum boyut
        final_w = max(100, final_w)
        final_h = max(100, final_h)
        
        # Pozisyon hesapla (merkez + user offset)
        center_x = (ow - final_w) // 2
        center_y = (oh - final_h) // 2
        
        pos_x = center_x + self.transform.pos_x
        pos_y = center_y + self.transform.pos_y
        
        # Sınırları kontrol et
        # Video çerçeveden küçükse:  0 .. (ow-final_w)
        # Video çerçeveden büyükse: (ow-final_w) .. 0 (kırpma için)
        min_x = min(0, ow - final_w)
        max_x = max(0, ow - final_w)
        min_y = min(0, oh - final_h)
        max_y = max(0, oh - final_h)

        pos_x = max(min_x, min(max_x, pos_x))
        pos_y = max(min_y, min(max_y, pos_y))
        
        mode = self.transform.bg_mode
        
        if mode == "blur":
            # Blur arka plan - video'yu blur edip arka plana koy
            blur = self.transform.bg_blur_strength
            filter_str = (
                f"split[bg][fg];"
                f"[bg]scale={ow}:{oh}:force_original_aspect_ratio=increase,"
                f"crop={ow}:{oh},"
                f"boxblur={blur}:2[blurred];"
                f"[fg]scale={final_w}:{final_h}[scaled];"
                f"[blurred][scaled]overlay={pos_x}:{pos_y}"
            )
        
        elif mode == "gradient":
            start_color = self.transform.bg_gradient_start
            filter_str = (
                f"scale={final_w}:{final_h}[v];"
                f"color=c=0x{start_color}:s={ow}x{oh}:d=1[bg];"
                f"[bg][v]overlay={pos_x}:{pos_y}:shortest=1"
            )
        
        elif mode == "color":
            color = self.transform.bg_color
            filter_str = (
                f"scale={final_w}:{final_h}[v];"
                f"color=c=0x{color}:s={ow}x{oh}:d=1[bg];"
                f"[bg][v]overlay={pos_x}:{pos_y}:shortest=1"
            )
        
        else:  # black
            # Siyah arka plan için de color+overlay kullan
            # Böylece video büyük olduğunda da (zoom/kırpma) pad hatası olmaz
            filter_str = (
                f"scale={final_w}:{final_h}[v];"
                f"color=c=black:s={ow}x{oh}:d=1[bg];"
                f"[bg][v]overlay={pos_x}:{pos_y}:shortest=1"
            )
        
        logger.debug(f"FFmpeg filter ({mode}): {filter_str}")
        logger.debug(f"Input: {vw}x{vh}, Output: {ow}x{oh}, Video: {final_w}x{final_h}, Pos: {pos_x},{pos_y}")
        return filter_str
    
    def export_short(
        self,
        output_path: Path,
        start_time: float,
        duration: float,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> bool:
        """Short video export et"""
        if self.frame_reader is None:
            logger.error("Video yüklenmemiş!")
            return False
        
        video_path = self.frame_reader.video_path
        vf = self.build_ffmpeg_filter()
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            "ffmpeg",
            "-ss", str(start_time),
            "-i", str(video_path),
            "-t", str(duration),
            "-vf", vf,
            "-c:v", "libx264",
            "-preset", self.transform.preset,
            "-crf", str(self.transform.crf),
            "-c:a", "aac",
            "-b:a", "128k",
            "-y",
            str(output_path)
        ]
        
        logger.info(f"Export başlıyor: {output_path.name}")
        logger.debug(f"Komut: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"✓ Export tamamlandı: {output_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg hatası: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Export hatası: {e}")
            return False
    
    @property
    def video_info(self) -> Optional[dict]:
        """Video bilgileri"""
        if self.frame_reader is None:
            return None
        
        return {
            "path": self.frame_reader.video_path,
            "width": self.frame_reader.width,
            "height": self.frame_reader.height,
            "duration": self.frame_reader.duration,
            "fps": self.frame_reader.fps,
            "total_frames": self.frame_reader.total_frames
        }
    
    def close(self):
        """Kaynakları serbest bırak"""
        if self.frame_reader:
            self.frame_reader.close()
            self.frame_reader = None
    
    def suggest_segments(
        self,
        segment_length: float = 60.0,
        max_segments: int = 10
    ) -> list:
        """
        Basit otomatik kesit önerisi üretir.
        
        - Video süresini frame_reader'dan alır
        - segment_length saniyelik parçalar halinde böler
        - max_segments ile sınırlar
        - Hiçbir FFmpeg çağrısı yapmaz, sadece hesaplama yapar
        
        Returns:
            List of dicts: [{"index": 1, "start": 0.0, "duration": 60.0}, ...]
        """
        if not self.frame_reader or self.frame_reader.duration <= 0:
            return []

        try:
            total = float(self.frame_reader.duration)
        except Exception:
            return []

        # Güvenli sınırlar
        try:
            seg_len = float(segment_length)
        except Exception:
            seg_len = 60.0

        if seg_len <= 1:
            seg_len = 10.0  # en az 10sn

        try:
            max_seg = int(max_segments)
        except Exception:
            max_seg = 10

        if max_seg < 1:
            max_seg = 1

        segments = []
        t = 0.0
        idx = 1

        while t < total and idx <= max_seg:
            remaining = total - t
            dur = seg_len if remaining > seg_len else remaining
            if dur < 2.0:
                break

            segments.append({
                "index": idx,
                "start": t,
                "duration": dur,
            })

            t += seg_len
            idx += 1

        return segments
