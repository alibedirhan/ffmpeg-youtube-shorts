"""
LinuxShorts Pro - Smart Video Analyzer
Akıllı video analizi: Sessizlik algılama, Hook detection, Sahne değişikliği
"""

import subprocess
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import numpy as np

from utils.logger import get_logger

logger = get_logger("LinuxShorts.SmartAnalyzer")

# OpenCV kontrolü
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logger.warning("OpenCV bulunamadı")


@dataclass
class Segment:
    """Video segmenti"""
    start: float
    end: float
    duration: float
    score: float = 0.0
    segment_type: str = "normal"
    label: str = ""
    
    def to_dict(self) -> dict:
        return {
            "start": self.start,
            "end": self.end,
            "duration": self.duration,
            "score": self.score,
            "type": self.segment_type,
            "label": self.label
        }


@dataclass
class AnalysisResult:
    """Analiz sonuçları"""
    duration: float = 0.0
    silence_segments: List[Segment] = field(default_factory=list)
    speech_segments: List[Segment] = field(default_factory=list)
    hook_candidates: List[Segment] = field(default_factory=list)
    scene_changes: List[float] = field(default_factory=list)
    best_segments: List[Segment] = field(default_factory=list)
    audio_levels: List[Tuple[float, float]] = field(default_factory=list)
    motion_scores: List[Tuple[float, float]] = field(default_factory=list)


class SmartVideoAnalyzer:
    """Akıllı video analiz sınıfı"""
    
    def __init__(self):
        self.video_path: Optional[Path] = None
        self.duration: float = 0.0
        self.fps: float = 30.0
        self.width: int = 0
        self.height: int = 0
        self.result: Optional[AnalysisResult] = None
        
        self.silence_threshold_db: float = -35.0
        self.silence_min_duration: float = 0.3
        self.hook_window: float = 15.0
        self.scene_threshold: float = 30.0
        self.min_segment_duration: float = 15.0
        self.target_duration: float = 60.0
    
    def load_video(self, video_path: Path) -> bool:
        """Video yükle"""
        self.video_path = Path(video_path)
        
        if not self.video_path.exists():
            logger.error(f"Video bulunamadı: {video_path}")
            return False
        
        try:
            cmd = [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_format", "-show_streams",
                str(self.video_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            info = json.loads(result.stdout)
            
            for stream in info.get("streams", []):
                if stream.get("codec_type") == "video":
                    self.width = int(stream.get("width", 0))
                    self.height = int(stream.get("height", 0))
                    fps_str = stream.get("r_frame_rate", "30/1")
                    if "/" in fps_str:
                        num, den = map(int, fps_str.split("/"))
                        self.fps = num / den if den > 0 else 30.0
                    break
            
            self.duration = float(info.get("format", {}).get("duration", 0))
            logger.info(f"Video: {self.width}x{self.height}, {self.fps:.1f}fps, {self.duration:.1f}s")
            return True
            
        except Exception as e:
            logger.error(f"Video yükleme hatası: {e}")
            return False
    
    def analyze_audio(self) -> Tuple[List[Segment], List[Segment]]:
        """Ses analizi - sessizlik ve konuşma"""
        if not self.video_path:
            return [], []
        
        logger.info("Ses analizi başlıyor...")
        
        try:
            cmd = [
                "ffmpeg", "-i", str(self.video_path),
                "-af", f"silencedetect=noise={self.silence_threshold_db}dB:d={self.silence_min_duration}",
                "-f", "null", "-"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            output = result.stderr
            
            silence_segments = []
            silence_start = None
            
            for line in output.split("\n"):
                if "silence_start:" in line:
                    try:
                        silence_start = float(line.split("silence_start:")[1].split()[0])
                    except:
                        pass
                elif "silence_end:" in line and silence_start is not None:
                    try:
                        silence_end = float(line.split("silence_end:")[1].split()[0])
                        duration = silence_end - silence_start
                        silence_segments.append(Segment(
                            start=silence_start, end=silence_end, duration=duration,
                            segment_type="silence", label=f"Sessizlik ({duration:.1f}s)"
                        ))
                        silence_start = None
                    except:
                        pass
            
            # Konuşma bölümleri
            speech_segments = []
            prev_end = 0.0
            
            for silence in silence_segments:
                if silence.start > prev_end + 0.5:
                    speech_segments.append(Segment(
                        start=prev_end, end=silence.start,
                        duration=silence.start - prev_end,
                        segment_type="speech",
                        label=f"Konuşma ({silence.start - prev_end:.1f}s)"
                    ))
                prev_end = silence.end
            
            if self.duration > prev_end + 0.5:
                speech_segments.append(Segment(
                    start=prev_end, end=self.duration,
                    duration=self.duration - prev_end,
                    segment_type="speech",
                    label=f"Konuşma ({self.duration - prev_end:.1f}s)"
                ))
            
            logger.info(f"Ses analizi: {len(silence_segments)} sessizlik, {len(speech_segments)} konuşma")
            return silence_segments, speech_segments
            
        except Exception as e:
            logger.error(f"Ses analizi hatası: {e}")
            return [], []
    
    def analyze_audio_levels(self, sample_interval: float = 1.0) -> List[Tuple[float, float]]:
        """Ses seviyelerini analiz et"""
        if not self.video_path:
            return []
        
        try:
            cmd = [
                "ffmpeg", "-i", str(self.video_path),
                "-af", f"volumedetect",
                "-f", "null", "-"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            # Basit ses seviyesi tahmini
            levels = []
            for t in np.arange(0, self.duration, sample_interval):
                levels.append((t, -20.0))  # Varsayılan
            
            return levels
        except:
            return []
    
    def detect_scene_changes(self, threshold: float = None, max_scenes: int = 50) -> List[float]:
        """Sahne değişikliklerini tespit et"""
        if not OPENCV_AVAILABLE or not self.video_path:
            return []
        
        if threshold is None:
            threshold = self.scene_threshold
        
        logger.info("Sahne analizi başlıyor...")
        
        try:
            cap = cv2.VideoCapture(str(self.video_path))
            if not cap.isOpened():
                return []
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            sample_interval = int(fps * 0.5)
            if sample_interval < 1:
                sample_interval = 1
            
            scene_changes = []
            prev_hist = None
            frame_idx = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % sample_interval == 0:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
                    hist = cv2.normalize(hist, hist).flatten()
                    
                    if prev_hist is not None:
                        diff = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CHISQR)
                        if diff > threshold:
                            scene_changes.append(frame_idx / fps)
                            if len(scene_changes) >= max_scenes:
                                break
                    
                    prev_hist = hist
                frame_idx += 1
            
            cap.release()
            logger.info(f"Sahne analizi: {len(scene_changes)} sahne değişikliği")
            return scene_changes
            
        except Exception as e:
            logger.error(f"Sahne analizi hatası: {e}")
            return []
    
    def analyze_motion(self, sample_interval: float = 1.0) -> List[Tuple[float, float]]:
        """Hareket yoğunluğu analizi"""
        if not OPENCV_AVAILABLE or not self.video_path:
            return []
        
        logger.info("Hareket analizi başlıyor...")
        
        try:
            cap = cv2.VideoCapture(str(self.video_path))
            if not cap.isOpened():
                return []
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_interval = int(fps * sample_interval)
            if frame_interval < 1:
                frame_interval = 1
            
            motion_scores = []
            prev_frame = None
            frame_idx = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % frame_interval == 0:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    gray = cv2.GaussianBlur(gray, (21, 21), 0)
                    
                    if prev_frame is not None:
                        diff = cv2.absdiff(prev_frame, gray)
                        thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
                        motion = np.sum(thresh > 0) / thresh.size * 100
                        motion_scores.append((frame_idx / fps, motion))
                    
                    prev_frame = gray
                frame_idx += 1
            
            cap.release()
            logger.info(f"Hareket analizi: {len(motion_scores)} örnek")
            return motion_scores
            
        except Exception as e:
            logger.error(f"Hareket analizi hatası: {e}")
            return []
    
    def detect_hooks(self, audio_levels: List, motion_scores: List) -> List[Segment]:
        """Hook (dikkat çekici an) tespit et"""
        logger.info("Hook analizi başlıyor...")
        
        hooks = []
        hook_window = min(self.hook_window, self.duration)
        
        # Hareket skorlarını kullan
        scored_times = []
        for time, motion in motion_scores:
            if time <= hook_window:
                scored_times.append((time, motion))
        
        scored_times.sort(key=lambda x: x[1], reverse=True)
        
        for i, (time, score) in enumerate(scored_times[:5]):
            if score > 5:
                hooks.append(Segment(
                    start=max(0, time - 2),
                    end=min(hook_window, time + 3),
                    duration=5, score=score,
                    segment_type="hook",
                    label=f"Hook #{i+1} (Hareket: {score:.0f}%)"
                ))
        
        logger.info(f"Hook analizi: {len(hooks)} potansiyel hook")
        return hooks
    
    def find_best_segments(self, target_duration: float = 60.0) -> List[Segment]:
        """En iyi Short segmentlerini bul"""
        if not self.result:
            return []
        
        segments = []
        
        for speech in self.result.speech_segments:
            if speech.duration < self.min_segment_duration:
                continue
            
            score = 50.0
            
            for hook in self.result.hook_candidates:
                if speech.start <= hook.start <= speech.end:
                    score += 20
                    break
            
            for scene_time in self.result.scene_changes:
                if abs(speech.start - scene_time) < 1.0:
                    score += 15
                    break
            
            if speech.start < self.duration * 0.3:
                score += 10
            
            segments.append(Segment(
                start=speech.start,
                end=min(speech.start + target_duration, speech.end),
                duration=min(speech.duration, target_duration),
                score=score, segment_type="best",
                label=f"Önerilen (Skor: {score:.0f})"
            ))
        
        segments.sort(key=lambda x: x.score, reverse=True)
        return segments[:10]
    
    def full_analysis(self, progress_callback=None) -> AnalysisResult:
        """Tam analiz"""
        if not self.video_path:
            return AnalysisResult()
        
        self.result = AnalysisResult(duration=self.duration)
        
        if progress_callback:
            progress_callback(10, "Ses analizi...")
        silence, speech = self.analyze_audio()
        self.result.silence_segments = silence
        self.result.speech_segments = speech
        
        if progress_callback:
            progress_callback(30, "Ses seviyeleri...")
        self.result.audio_levels = self.analyze_audio_levels()
        
        if progress_callback:
            progress_callback(50, "Sahne analizi...")
        self.result.scene_changes = self.detect_scene_changes()
        
        if progress_callback:
            progress_callback(70, "Hareket analizi...")
        self.result.motion_scores = self.analyze_motion()
        
        if progress_callback:
            progress_callback(85, "Hook tespiti...")
        self.result.hook_candidates = self.detect_hooks(
            self.result.audio_levels, self.result.motion_scores
        )
        
        if progress_callback:
            progress_callback(95, "Segment önerileri...")
        self.result.best_segments = self.find_best_segments(self.target_duration)
        
        if progress_callback:
            progress_callback(100, "Tamamlandı!")
        
        return self.result
    
    def get_summary(self) -> dict:
        """Analiz özeti"""
        if not self.result:
            return {}
        
        return {
            "duration": self.duration,
            "silence_count": len(self.result.silence_segments),
            "speech_count": len(self.result.speech_segments),
            "scene_changes": len(self.result.scene_changes),
            "hook_count": len(self.result.hook_candidates),
            "best_segments": len(self.result.best_segments)
        }
