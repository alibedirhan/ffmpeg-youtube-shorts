"""
LinuxShorts Generator - Video Analyzer
Akıllı kesit önerisi için video analizi
"""

import subprocess
import json
from pathlib import Path
from typing import List, Tuple, Dict
from dataclasses import dataclass
import statistics

from utils.logger import get_logger

logger = get_logger("LinuxShorts.Analyzer")


@dataclass
class VideoSegment:
    """Önerilen video segmenti"""
    start_time: str      # HH:MM:SS formatında
    end_time: str        # HH:MM:SS formatında
    duration: float      # Saniye cinsinden
    score: float         # Viral potansiyel skoru (0-100)
    reason: str          # Neden önerildi
    category: str        # Kategori


class VideoAnalyzer:
    """Video analiz ve kesit önerisi sınıfı"""
    
    def __init__(self):
        """Video analyzer başlatıcı"""
        logger.info("Video Analyzer başlatıldı")
    
    def analyze_audio_levels(self, video_path: Path) -> List[Tuple[float, float]]:
        """
        Video'nun ses seviyelerini analiz eder
        
        Args:
            video_path: Video dosyası
            
        Returns:
            [(zaman, ses_seviyesi)] listesi
        """
        logger.info("Ses seviyeleri analiz ediliyor...")
        
        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-af", "volumedetect",
            "-f", "null",
            "/dev/null"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                stderr=subprocess.STDOUT
            )
            
            # FFmpeg çıktısından ses bilgilerini parse et
            output = result.stdout
            
            # mean_volume ve max_volume bul
            mean_volume = -30.0  # Default
            for line in output.split('\n'):
                if 'mean_volume:' in line:
                    try:
                        mean_volume = float(line.split(':')[1].strip().split()[0])
                    except:
                        pass
            
            logger.info(f"Ortalama ses seviyesi: {mean_volume} dB")
            
            return [(0, mean_volume)]  # Basitleştirilmiş
            
        except Exception as e:
            logger.error(f"Ses analizi hatası: {e}")
            return []
    
    def detect_scene_changes(self, video_path: Path) -> List[float]:
        """
        Sahne değişikliklerini tespit eder
        
        Args:
            video_path: Video dosyası
            
        Returns:
            Sahne değişimi zamanları (saniye)
        """
        logger.info("Sahne değişiklikleri tespit ediliyor...")
        
        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-filter:v", "select='gt(scene,0.3)',showinfo",
            "-f", "null",
            "/dev/null"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                stderr=subprocess.STDOUT
            )
            
            output = result.stdout
            scene_times = []
            
            # showinfo çıktısından zamanları parse et
            for line in output.split('\n'):
                if 'pts_time:' in line:
                    try:
                        time_str = line.split('pts_time:')[1].split()[0]
                        scene_times.append(float(time_str))
                    except:
                        pass
            
            logger.info(f"✓ {len(scene_times)} sahne değişimi tespit edildi")
            return scene_times[:20]  # İlk 20'si
            
        except Exception as e:
            logger.error(f"Sahne tespiti hatası: {e}")
            return []
    
    def detect_silence(self, video_path: Path) -> List[Tuple[float, float]]:
        """
        Sessiz bölümleri tespit eder
        
        Args:
            video_path: Video dosyası
            
        Returns:
            [(başlangıç, bitiş)] sessiz bölümler
        """
        logger.info("Sessiz bölümler tespit ediliyor...")
        
        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-af", "silencedetect=noise=-30dB:d=1",
            "-f", "null",
            "/dev/null"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                stderr=subprocess.STDOUT
            )
            
            output = result.stdout
            silences = []
            
            silence_start = None
            for line in output.split('\n'):
                if 'silence_start:' in line:
                    try:
                        silence_start = float(line.split('silence_start:')[1].strip())
                    except:
                        pass
                elif 'silence_end:' in line and silence_start is not None:
                    try:
                        silence_end = float(line.split('silence_end:')[1].split('|')[0].strip())
                        silences.append((silence_start, silence_end))
                        silence_start = None
                    except:
                        pass
            
            logger.info(f"✓ {len(silences)} sessiz bölüm tespit edildi")
            return silences
            
        except Exception as e:
            logger.error(f"Sessizlik tespiti hatası: {e}")
            return []
    
    def suggest_segments(
        self,
        video_path: Path,
        video_duration: float,
        target_duration: float = 60.0
    ) -> List[VideoSegment]:
        """
        Video için akıllı kesit önerileri üretir
        
        Args:
            video_path: Video dosyası
            video_duration: Video süresi (saniye)
            target_duration: Hedef short süresi (saniye)
            
        Returns:
            Önerilen segmentler listesi
        """
        logger.info(f"Video analiz ediliyor: {video_path.name}")
        logger.info(f"Süre: {video_duration}s, Hedef: {target_duration}s")
        
        segments = []
        
        # 1. Sahne değişimlerini tespit et
        scene_changes = self.detect_scene_changes(video_path)
        
        # 2. Sessiz bölümleri tespit et
        silences = self.detect_silence(video_path)
        
        # 3. Segmentleri oluştur
        num_segments = int(video_duration / target_duration)
        
        for i in range(min(num_segments, 5)):  # En fazla 5 öneri
            # Eşit aralıklarla böl
            start = i * (video_duration / num_segments)
            end = start + target_duration
            
            # Video sonunu aşma
            if end > video_duration:
                end = video_duration
                start = max(0, end - target_duration)
            
            # Skor hesapla
            score = self._calculate_score(
                start, end, scene_changes, silences
            )
            
            # Kategorize et
            category = self._categorize_segment(score)
            reason = self._generate_reason(score, scene_changes, silences, start, end)
            
            segments.append(VideoSegment(
                start_time=self._seconds_to_time(start),
                end_time=self._seconds_to_time(end),
                duration=end - start,
                score=score,
                reason=reason,
                category=category
            ))
        
        # Skora göre sırala (en yüksek önce)
        segments.sort(key=lambda x: x.score, reverse=True)
        
        logger.info(f"✓ {len(segments)} segment önerisi oluşturuldu")
        return segments
    
    def _calculate_score(
        self,
        start: float,
        end: float,
        scene_changes: List[float],
        silences: List[Tuple[float, float]]
    ) -> float:
        """
        Segment için viral potansiyel skoru hesaplar
        
        Returns:
            Skor (0-100)
        """
        score = 50.0  # Başlangıç skoru
        
        # Sahne değişimi sayısı (daha fazla = daha ilgi çekici)
        scenes_in_segment = [s for s in scene_changes if start <= s <= end]
        scene_score = min(len(scenes_in_segment) * 5, 25)
        score += scene_score
        
        # Sessizlik oranı (daha az = daha iyi)
        silence_duration = sum(
            min(se, end) - max(ss, start)
            for ss, se in silences
            if not (se < start or ss > end)
        )
        silence_ratio = silence_duration / (end - start)
        silence_penalty = silence_ratio * 30
        score -= silence_penalty
        
        # Video başı bonusu (ilk 2 dakika daha değerli)
        if start < 120:
            score += 10
        
        # Video sonu bonusu (son özet kısımları)
        if start > (end * 0.8):
            score += 5
        
        return max(0, min(100, score))
    
    def _categorize_segment(self, score: float) -> str:
        """Skora göre kategori belirler"""
        if score >= 75:
            return "🔥🔥🔥 Çok Yüksek Potansiyel"
        elif score >= 60:
            return "🔥🔥 Yüksek Potansiyel"
        elif score >= 45:
            return "🔥 Orta Potansiyel"
        else:
            return "📊 Düşük Potansiyel"
    
    def _generate_reason(
        self,
        score: float,
        scene_changes: List[float],
        silences: List[Tuple[float, float]],
        start: float,
        end: float
    ) -> str:
        """Öneri sebebini açıklar"""
        reasons = []
        
        scenes_in_segment = [s for s in scene_changes if start <= s <= end]
        if len(scenes_in_segment) > 2:
            reasons.append(f"Dinamik içerik ({len(scenes_in_segment)} sahne)")
        
        silence_duration = sum(
            min(se, end) - max(ss, start)
            for ss, se in silences
            if not (se < start or ss > end)
        )
        
        if silence_duration < 5:
            reasons.append("Sürekli konuşma/aksiyon")
        
        if start < 120:
            reasons.append("Video başı (hook bölgesi)")
        
        if not reasons:
            reasons.append("Dengeli içerik akışı")
        
        return ", ".join(reasons)
    
    def _seconds_to_time(self, seconds: float) -> str:
        """Saniyeyi HH:MM:SS formatına çevirir"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"


# Test kodu
if __name__ == "__main__":
    analyzer = VideoAnalyzer()
    print("✅ Video Analyzer hazır!")
    print("\nKullanım:")
    print("  segments = analyzer.suggest_segments(video_path, duration)")
    print("  for seg in segments:")
    print("    print(f'{seg.category}: {seg.start_time}-{seg.end_time}')")
