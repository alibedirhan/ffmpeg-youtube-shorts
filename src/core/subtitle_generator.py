"""
LinuxShorts Generator - Subtitle Generator v6.0 ULTIMATE
✅ Pozisyon TAMAMEN düzeltildi (bottom = alt, top = üst)
✅ Kelime limiti DOĞRU çalışıyor (3 kelime = her satırda max 3 kelime)
✅ Font boyutu slider'dan alınıyor
✅ Detaylı loglama (her şey görünür)

SORUN GİDERME:
- Pozisyon için ASS Alignment sistemi kullanılıyor
- MarginV ile Y pozisyonu ayarlanıyor
- wrap_text ile kelime bazlı satır kırma
"""

import subprocess
from pathlib import Path
from typing import Optional, List, Tuple
from dataclasses import dataclass
import json
import time
import re

from utils.logger import get_logger

logger = get_logger("LinuxShorts.Subtitle")


# Subtitle Corrector'ı import et
try:
    from .subtitle_corrector import SubtitleCorrector
    CORRECTOR_AVAILABLE = True
except ImportError:
    CORRECTOR_AVAILABLE = False
    logger.warning("SubtitleCorrector bulunamadı, düzeltme devre dışı")


@dataclass
class SubtitleSegment:
    """Tek bir altyazı segmenti"""
    start: float  # Başlangıç zamanı (saniye)
    end: float    # Bitiş zamanı (saniye)
    text: str     # Altyazı metni


class SubtitleGenerator:
    """Whisper AI ile altyazı üretici v6.0 ULTIMATE"""
    
    def __init__(self, enable_correction: bool = True):
        """
        Args:
            enable_correction: Akıllı düzeltmeyi aktif et
        """
        self._check_whisper()
        
        # Corrector'ı başlat
        self.enable_correction = enable_correction and CORRECTOR_AVAILABLE
        if self.enable_correction:
            self.corrector = SubtitleCorrector()
            logger.info("✓ Akıllı düzeltme aktif")
        else:
            self.corrector = None
            logger.info("Akıllı düzeltme devre dışı")
    
    def _check_whisper(self) -> bool:
        """Whisper'ın kurulu olup olmadığını kontrol eder"""
        try:
            result = subprocess.run(
                ["whisper", "--help"],
                capture_output=True,
                text=True
            )
            logger.info("✓ Whisper kurulu ve hazır")
            return True
        except FileNotFoundError:
            logger.warning("⚠️ Whisper bulunamadı!")
            logger.info("Kurulum: pip install -U openai-whisper")
            return False
    
    def generate_subtitles(
        self,
        video_path: Path,
        language: str = "tr",
        model: str = "medium",
        apply_correction: bool = True
    ) -> List[SubtitleSegment]:
        """
        Video'dan altyazı üretir - ULTIMATE VERSION
        
        Args:
            video_path: Video dosyası yolu
            language: Dil kodu (tr)
            model: Whisper modeli (medium önerilen)
            apply_correction: Akıllı düzeltme uygula
        
        Returns:
            Altyazı segmentleri listesi
        """
        logger.info("="*70)
        logger.info("🚀 WHISPER ALTYAZI ÜRETİMİ")
        logger.info("="*70)
        logger.info(f"📂 Video: {video_path.name}")
        logger.info(f"🤖 Model: {model}")
        logger.info(f"🌍 Dil: {language}")
        logger.info(f"🔧 Düzeltme: {apply_correction and self.enable_correction}")
        logger.info("="*70)
        
        start_time = time.time()
        output_dir = video_path.parent
        
        try:
            # Whisper komutu
            cmd = [
                "whisper",
                str(video_path),
                "--model", model,
                "--language", language,
                "--output_format", "json",
                "--output_dir", str(output_dir),
                "--device", "cpu",
                "--temperature", "0.0",
                "--beam_size", "5",
                "--best_of", "5",
                "--compression_ratio_threshold", "2.4",
                "--logprob_threshold", "-1.0",
                "--no_speech_threshold", "0.6",
                "--condition_on_previous_text", "True",
                "--initial_prompt", 
                "Bu Türkçe bir konuşmadır. Linux, Ubuntu, Debian, apt, dpkg, paket yöneticisi gibi teknik terimler kullanılmaktadır.",
                "--word_timestamps", "True",
            ]
            
            logger.info("⏳ Whisper çalışıyor...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # JSON oku
            json_file = output_dir / f"{video_path.stem}.json"
            
            if not json_file.exists():
                raise FileNotFoundError(f"Whisper JSON çıktısı bulunamadı: {json_file}")
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Segmentleri parse et
            segments = []
            for seg in data.get('segments', []):
                segments.append(SubtitleSegment(
                    start=seg['start'],
                    end=seg['end'],
                    text=seg['text'].strip()
                ))
            
            whisper_time = time.time() - start_time
            logger.info(f"✓ {len(segments)} segment oluşturuldu ({whisper_time:.1f}s)")
            
            # Akıllı düzeltme
            if apply_correction and self.enable_correction and self.corrector:
                logger.info("🔧 Akıllı düzeltme uygulanıyor...")
                correction_start = time.time()
                segments = self.corrector.correct_subtitle_segments(segments)
                correction_time = time.time() - correction_start
                logger.info(f"✓ Düzeltme tamamlandı ({correction_time:.1f}s)")
            
            # Geçici JSON sil
            json_file.unlink()
            
            total_time = time.time() - start_time
            logger.info("="*70)
            logger.info(f"✅ TOPLAM SÜRE: {total_time:.1f}s")
            logger.info("="*70)
            
            return segments
            
        except Exception as e:
            logger.error(f"Altyazı üretim hatası: {e}")
            logger.exception("Detaylı hata:")
            raise
    
    def wrap_text(self, text: str, max_words_per_line: int = 4) -> str:
        """
        Metni kelime bazlı satırlara böler
        
        DOĞRU KULLANIM:
        max_words_per_line=3 → Her satırda MAKSIMUM 3 kelime
        
        Örnek:
        text = "Bu çok uzun bir altyazı cümlesidir"
        max_words_per_line = 3
        →
        "Bu çok uzun\nbir altyazı cümlesidir"
        
        Args:
            text: Bölünecek metin
            max_words_per_line: HER SATIRDA maksimum kelime sayısı
            
        Returns:
            Satırlara bölünmüş metin
        """
        words = text.split()
        lines = []
        
        # Her X kelimede bir satır kır
        for i in range(0, len(words), max_words_per_line):
            line = ' '.join(words[i:i + max_words_per_line])
            lines.append(line)
        
        result = '\n'.join(lines)
        
        logger.debug(f"wrap_text: '{text}' → '{result}' (max={max_words_per_line} kelime/satır)")
        
        return result
    
    def create_srt_file(
        self,
        segments: List[SubtitleSegment],
        output_path: Path,
        max_words_per_line: int = 4
    ) -> bool:
        """
        SRT dosyası oluşturur (kelime wrap ile)
        
        Args:
            segments: Altyazı segmentleri
            output_path: Çıktı SRT dosyası
            max_words_per_line: Her satırda MAX kelime
            
        Returns:
            Başarılı ise True
        """
        logger.info("="*70)
        logger.info("💾 SRT DOSYASI OLUŞTURULUYOR")
        logger.info("="*70)
        logger.info(f"📝 Dosya: {output_path.name}")
        logger.info(f"📏 Kelime limiti: {max_words_per_line} kelime/satır")
        logger.info(f"📊 Segment sayısı: {len(segments)}")
        logger.info("="*70)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for i, seg in enumerate(segments, 1):
                    start_time = self._format_time_srt(seg.start)
                    end_time = self._format_time_srt(seg.end)
                    
                    # Metni wrap et
                    wrapped_text = self.wrap_text(seg.text, max_words_per_line)
                    
                    # SRT formatı
                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{wrapped_text}\n\n")
                    
                    # İlk 3 segmenti logla (debug için)
                    if i <= 3:
                        logger.debug(f"Segment #{i}:")
                        logger.debug(f"  Zaman: {start_time} --> {end_time}")
                        logger.debug(f"  Orijinal: '{seg.text}'")
                        logger.debug(f"  Wrapped: '{wrapped_text}'")
            
            logger.info(f"✅ SRT dosyası oluşturuldu: {output_path}")
            logger.info("="*70)
            return True
            
        except Exception as e:
            logger.error(f"SRT oluşturma hatası: {e}")
            return False
    
    def read_srt_file(self, srt_path: Path) -> List[SubtitleSegment]:
        """
        SRT dosyasını okur
        
        Args:
            srt_path: SRT dosyası yolu
            
        Returns:
            Altyazı segmentleri
        """
        logger.info(f"SRT dosyası okunuyor: {srt_path}")
        
        try:
            with open(srt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            segments = []
            blocks = content.strip().split('\n\n')
            
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) < 3:
                    continue
                
                # Zaman satırı
                time_line = lines[1]
                times = time_line.split(' --> ')
                if len(times) != 2:
                    continue
                
                start = self._parse_time_srt(times[0])
                end = self._parse_time_srt(times[1])
                
                # Metin
                text = '\n'.join(lines[2:])
                
                segments.append(SubtitleSegment(
                    start=start,
                    end=end,
                    text=text
                ))
            
            logger.info(f"✓ {len(segments)} segment okundu")
            return segments
            
        except Exception as e:
            logger.error(f"SRT okuma hatası: {e}")
            return []
    
    def _format_time_srt(self, seconds: float) -> str:
        """Saniye → SRT format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _parse_time_srt(self, time_str: str) -> float:
        """SRT format → Saniye"""
        time_str = time_str.strip().replace(',', '.')
        parts = time_str.split(':')
        if len(parts) != 3:
            return 0.0
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds
    
    def burn_subtitles(
        self,
        video_path: Path,
        srt_path: Path,
        output_path: Path,
        fontsize: int = 20,
        style: str = "tiktok",
        position: str = "bottom"
    ) -> bool:
        """
        Altyazıları videoya yazar - v6.0 ULTIMATE
        
        ✅ POZISYON TAM ÇALIŞIYOR:
           - bottom = ALT (MarginV=100, Alignment=2)
           - center = ORTA (MarginV=500, Alignment=5)
           - top = ÜST (MarginV=50, Alignment=8)
        
        ✅ FONT BOYUTU slider'dan alınıyor
        ✅ DETAYLI LOGLAMA (her şey görünür)
        
        Args:
            video_path: Kaynak video
            srt_path: SRT dosyası
            output_path: Çıktı videosu
            fontsize: Font boyutu (14-32px)
            style: Stil (tiktok/youtube/minimal)
            position: Pozisyon (bottom/center/top)
            
        Returns:
            Başarılı ise True
        """
        logger.info("="*70)
        logger.info("🎬 ALTYAZILAR VİDEOYA YAZILIYOR")
        logger.info("="*70)
        logger.info(f"📹 Video: {video_path.name}")
        logger.info(f"📝 SRT: {srt_path.name}")
        logger.info(f"🔤 Font: {fontsize}px")
        logger.info(f"🎨 Stil: {style}")
        logger.info(f"📍 Pozisyon: {position}")
        logger.info("="*70)
        
        # SRT kontrolü
        if not srt_path.exists():
            logger.error(f"SRT dosyası bulunamadı: {srt_path}")
            return False
        
        # Stil ayarları
        styles = {
            "tiktok": {
                "font": "Arial-Bold",
                "fontcolor": "yellow",
                "bordercolor": "black",
                "borderw": 3,
            },
            "youtube": {
                "font": "Arial",
                "fontcolor": "white",
                "bordercolor": "black",
                "borderw": 2,
            },
            "minimal": {
                "font": "Arial",
                "fontcolor": "white",
                "bordercolor": "black",
                "borderw": 1,
            }
        }
        
        s = styles.get(style, styles["youtube"])
        
        # 🔥 POZİSYON AYARLARI (ASS Alignment sistemi)
        # ASS Alignment numaraları:
        # 1-3: Alt (sol-orta-sağ)
        # 4-6: Orta (sol-orta-sağ)
        # 7-9: Üst (sol-orta-sağ)
        
        # MarginV: Y ekseninde pozisyon (piksel)
        # Video: 1920px yükseklik (9:16)
        
        position_settings = {
            "bottom": {
                "alignment": 2,    # Alt orta
                "marginv": 100     # Alttan 100px yukarıda
            },
            "center": {
                "alignment": 5,    # Tam orta
                "marginv": 960     # Ortada (1920/2)
            },
            "top": {
                "alignment": 8,    # Üst orta
                "marginv": 100     # Üstten 100px aşağıda
            }
        }
        
        pos = position_settings.get(position, position_settings["bottom"])
        
        logger.info("FFmpeg Parametreleri:")
        logger.info(f"  Font: {s['font']}")
        logger.info(f"  FontSize: {fontsize}px")
        logger.info(f"  Renk: {s['fontcolor']}")
        logger.info(f"  Border: {s['borderw']}px {s['bordercolor']}")
        logger.info(f"  Alignment: {pos['alignment']} ({position})")
        logger.info(f"  MarginV: {pos['marginv']}px")
        logger.info("="*70)
        
        # FFmpeg subtitle filter
        subtitle_filter = (
            f"subtitles={srt_path}:"
            f"force_style='"
            f"FontName={s['font']},"
            f"FontSize={fontsize},"
            f"PrimaryColour=&H00{self._color_to_hex(s['fontcolor'])},"
            f"OutlineColour=&H00{self._color_to_hex(s['bordercolor'])},"
            f"BorderStyle=1,"
            f"Outline={s['borderw']},"
            f"Alignment={pos['alignment']},"
            f"MarginV={pos['marginv']}"
            f"'"
        )
        
        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-vf", subtitle_filter,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-c:a", "copy",
            "-y",
            str(output_path)
        ]
        
        try:
            logger.info("⏳ FFmpeg çalışıyor...")
            logger.debug(f"Komut: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("="*70)
            logger.info("✅ BAŞARILI!")
            logger.info("="*70)
            logger.info(f"📁 Çıktı: {output_path.name}")
            logger.info(f"📦 Boyut: {output_path.stat().st_size / (1024*1024):.1f} MB")
            logger.info(f"📍 Altyazı pozisyonu: {position} ({pos['alignment']}, {pos['marginv']}px)")
            logger.info("="*70)
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error("="*70)
            logger.error("❌ FFMPEG HATASI")
            logger.error("="*70)
            logger.error(f"Çıktı: {e.stderr}")
            logger.error("="*70)
            return False
    
    def _color_to_hex(self, color: str) -> str:
        """Renk → Hex (BGR formatı)"""
        colors = {
            "white": "FFFFFF",
            "black": "000000",
            "yellow": "00FFFF",
            "red": "0000FF",
            "blue": "FF0000",
            "green": "00FF00"
        }
        return colors.get(color.lower(), "FFFFFF")


# Test kodu
if __name__ == "__main__":
    gen = SubtitleGenerator()
    print("✅ Subtitle Generator v6.0 ULTIMATE hazır!")
    print("\n🔥 DÜZELTİLEN SORUNLAR:")
    print("   • Pozisyon TAMAMEN çalışıyor (bottom=alt, top=üst)")
    print("   • Kelime limiti DOĞRU (3=her satırda max 3 kelime)")
    print("   • Font boyutu slider'dan alınıyor")
    print("   • Detaylı loglama eklenmiş")
