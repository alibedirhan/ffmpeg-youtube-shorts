"""
LinuxShorts Generator - FFmpeg Wrapper
Video işleme ve short oluşturma motoru
"""

import subprocess
import shutil
import re
from pathlib import Path
from typing import Optional, Tuple, Callable
from dataclasses import dataclass


@dataclass
class VideoInfo:
    """Video bilgileri"""
    duration: float  # Saniye cinsinden
    width: int
    height: int
    fps: float
    codec: str
    file_path: Path


class FFmpegWrapper:
    """FFmpeg ile video işleme sınıfı"""
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        """
        Args:
            ffmpeg_path: FFmpeg binary'sinin yolu
        """
        self.ffmpeg_path = ffmpeg_path
        self._check_ffmpeg()
    
    def _check_ffmpeg(self) -> None:
        """FFmpeg'in sistemde kurulu olup olmadığını kontrol eder"""
        if not shutil.which(self.ffmpeg_path):
            raise FileNotFoundError(
                "FFmpeg bulunamadı! Lütfen FFmpeg'i kurun:\n"
                "sudo apt install ffmpeg"
            )
    
    def get_video_info(self, video_path: Path) -> VideoInfo:
        """
        Video dosyası hakkında bilgi alır
        
        Args:
            video_path: Video dosyasının yolu
            
        Returns:
            VideoInfo objesi
        """
        from utils.logger import get_logger
        logger = get_logger("LinuxShorts.FFmpeg")
        
        logger.debug(f"Video analiz ediliyor: {video_path}")
        logger.debug(f"Dosya var mı? {video_path.exists()}")
        logger.debug(f"Dosya boyutu: {video_path.stat().st_size if video_path.exists() else 'N/A'}")
        
        # Önce video stream bilgilerini al
        cmd_video = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate,codec_name",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]
        
        # Sonra format (duration) bilgisini al
        cmd_format = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]
        
        logger.debug(f"Video stream komutu: {' '.join(cmd_video)}")
        logger.debug(f"Format komutu: {' '.join(cmd_format)}")
        
        try:
            # Video stream bilgilerini al
            result_video = subprocess.run(
                cmd_video,
                capture_output=True,
                text=True,
                check=True
            )
            
            video_output = result_video.stdout.strip()
            logger.debug(f"Video stream çıktısı:\n{video_output}")
            
            if not video_output:
                logger.error("Video stream bulunamadı! Bu dosya sadece ses içeriyor olabilir.")
                raise RuntimeError("Video stream bulunamadı. Bu dosya video içermiyor olabilir.")
            
            # Format bilgilerini al
            result_format = subprocess.run(
                cmd_format,
                capture_output=True,
                text=True,
                check=True
            )
            
            format_output = result_format.stdout.strip()
            logger.debug(f"Format çıktısı:\n{format_output}")
            
            # Video stream çıktısını parse et
            # FFprobe çıktı sırası: codec_name\nwidth\nheight\nfps
            lines = video_output.split('\n')
            logger.debug(f"Parse edilen satırlar: {lines}")
            
            if len(lines) < 4:
                logger.error(f"Yetersiz video bilgisi! Satır sayısı: {len(lines)}")
                raise RuntimeError("Video bilgileri eksik. Dosya bozuk olabilir.")
            
            try:
                # Doğru sıralama: codec, width, height, fps
                codec = lines[0].strip()
                width = int(lines[1].strip())
                height = int(lines[2].strip())
                
                # FPS parse et
                fps_str = lines[3].strip()
                if '/' in fps_str:
                    fps_parts = fps_str.split('/')
                    fps = int(fps_parts[0]) / int(fps_parts[1])
                else:
                    fps = float(fps_str)
                
                # Duration
                duration = float(format_output) if format_output else 0.0
                
            except (ValueError, IndexError) as e:
                logger.error(f"Parse hatası: {e}")
                logger.error(f"Video çıktısı: {video_output}")
                raise RuntimeError(f"Video bilgileri parse edilemedi: {e}")
            
            logger.info(f"✓ Video bilgileri başarıyla alındı:")
            logger.info(f"  Çözünürlük: {width}x{height}")
            logger.info(f"  Süre: {duration}s")
            logger.info(f"  FPS: {fps}")
            logger.info(f"  Codec: {codec}")
            
            return VideoInfo(
                duration=duration,
                width=width,
                height=height,
                fps=fps,
                codec=codec,
                file_path=video_path
            )
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFprobe komutu başarısız: {e.stderr}")
            raise RuntimeError(f"Video bilgisi alınamadı: {e.stderr}")
        except Exception as e:
            logger.error(f"Video bilgisi alma hatası: {e}")
            logger.exception("Detaylı hata:")
            raise
    
    def create_short(
        self,
        input_path: Path,
        output_path: Path,
        start_time: str,
        duration: str,
        width: int = 1080,
        height: int = 1920,
        crf: int = 23,
        preset: str = "medium",
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> bool:
        """
        Short video oluşturur (9:16 formatında)
        
        Args:
            input_path: Kaynak video
            output_path: Çıktı dosyası
            start_time: Başlangıç zamanı (HH:MM:SS formatında)
            duration: Süre (HH:MM:SS veya saniye)
            width: Çıktı genişliği (default: 1080)
            height: Çıktı yüksekliği (default: 1920)
            crf: Kalite (18-28, düşük = yüksek kalite)
            preset: FFmpeg preset (ultrafast, fast, medium, slow)
            progress_callback: İlerleme callback fonksiyonu
            
        Returns:
            Başarılı ise True
        """
        # Output dizinini oluştur
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # FFmpeg komutu
        cmd = [
            self.ffmpeg_path,
            "-i", str(input_path),
            "-ss", start_time,
            "-t", duration,
            "-vf", f"crop=ih*9/16:ih,scale={width}:{height}",
            "-c:v", "libx264",
            "-preset", preset,
            "-crf", str(crf),
            "-c:a", "aac",
            "-b:a", "128k",
            "-y",  # Overwrite output
            str(output_path)
        ]
        
        try:
            # Progress tracking için
            if progress_callback:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                # FFmpeg progress'i stderr'de
                for line in process.stderr:
                    # time=00:00:10.00 formatını yakala
                    if "time=" in line:
                        time_match = re.search(r'time=(\d{2}):(\d{2}):(\d{2}\.\d{2})', line)
                        if time_match:
                            h, m, s = time_match.groups()
                            current_time = int(h) * 3600 + int(m) * 60 + float(s)
                            
                            # Duration'ı saniyeye çevir
                            duration_seconds = self._time_to_seconds(duration)
                            progress = min(100, (current_time / duration_seconds) * 100)
                            progress_callback(progress)
                
                process.wait()
                
                if process.returncode != 0:
                    raise subprocess.CalledProcessError(
                        process.returncode,
                        cmd,
                        process.stderr.read()
                    )
            else:
                # Progress tracking olmadan
                subprocess.run(cmd, check=True, capture_output=True)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg hatası: {e.stderr if hasattr(e, 'stderr') else str(e)}")
            return False
    
    def _time_to_seconds(self, time_str: str) -> float:
        """
        Zaman string'ini saniyeye çevirir
        
        Args:
            time_str: "HH:MM:SS" veya "SS" formatında zaman
            
        Returns:
            Saniye cinsinden süre
        """
        if ":" in time_str:
            parts = time_str.split(":")
            if len(parts) == 3:
                h, m, s = parts
                return int(h) * 3600 + int(m) * 60 + float(s)
            elif len(parts) == 2:
                m, s = parts
                return int(m) * 60 + float(s)
        
        return float(time_str)
    
    def extract_audio(
        self,
        input_path: Path,
        output_path: Path
    ) -> bool:
        """
        Videodan ses çıkarır
        
        Args:
            input_path: Kaynak video
            output_path: Çıktı ses dosyası
            
        Returns:
            Başarılı ise True
        """
        cmd = [
            self.ffmpeg_path,
            "-i", str(input_path),
            "-vn",  # Video yok
            "-acodec", "libmp3lame",
            "-q:a", "2",  # Kalite
            "-y",
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def get_thumbnail(
        self,
        input_path: Path,
        output_path: Path,
        timestamp: str = "00:00:01"
    ) -> bool:
        """
        Videodan thumbnail oluşturur
        
        Args:
            input_path: Kaynak video
            output_path: Çıktı görsel dosyası
            timestamp: Hangi saniyeden alınacak
            
        Returns:
            Başarılı ise True
        """
        cmd = [
            self.ffmpeg_path,
            "-i", str(input_path),
            "-ss", timestamp,
            "-vframes", "1",
            "-y",
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False


# Test kodu
if __name__ == "__main__":
    # FFmpeg kontrolü
    wrapper = FFmpegWrapper()
    print(f"✅ FFmpeg kullanıma hazır!")
    
    # Örnek kullanım
    # video_info = wrapper.get_video_info(Path("test.mp4"))
    # print(f"Video: {video_info.width}x{video_info.height}, {video_info.duration}s")
