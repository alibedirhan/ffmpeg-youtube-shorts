"""
LinuxShorts Generator - Subtitle Corrector
Whisper altyazılarını akıllıca düzeltir (Türkçe + Linux terimleri)
"""

import re
from typing import List, Dict
from pathlib import Path

from utils.logger import get_logger

logger = get_logger("LinuxShorts.SubtitleCorrector")


class SubtitleCorrector:
    """Altyazı düzeltme sınıfı"""
    
    def __init__(self):
        """Düzeltme kurallarını yükle"""
        self.corrections = self._load_correction_rules()
        self.tech_terms = self._load_tech_terms()
        logger.info("Subtitle Corrector hazır")
    
    def _load_correction_rules(self) -> Dict[str, str]:
        """
        Yaygın Whisper hatalarını düzeltme kuralları
        
        Returns:
            {yanlış: doğru} dictionary
        """
        return {
            # 🔥 ALİ'NİN BULDUĞU HATALAR (Gerçek video'dan)
            "yönütücüsü": "yöneticisi",
            "yöneticesi": "yöneticisi",
            "yönütücü": "yönetici",
            "paket yöneticesi": "paket yöneticisi",
            "konutu": "konusu",
            "apt konutu": "apt konusu",
            "sağa üstünde": "sağ üstünde",
            "ilikten": "linkten",
            "linkten": "linkten",
            "İnternetlik": "interaktif",
            "sıkıntı": "script",
            "bir sıkıntı": "bir script",
            "İzlemenizde": "İzlemenizi de",
            "izlemenizde": "izlemenizi de",
            
            # Linux terimleri - küçük harf hataları
            "apete": "apt",
            "ap ti": "apt",
            "apite": "apt",
            "dıpıkıcı": "dpkg",
            "dipikici": "dpkg",
            "di pi ki ci": "dpkg",
            
            # Komut hataları
            "install komutu": "install komutu",
            "remove komutu": "remove komutu",
            "update komutu": "update komutu",
            "upgrade komutu": "upgrade komutu",
            
            # Teknik terimler
            "bağımlılık": "bağımlılık",
            "bağımlılıklar": "bağımlılıklar",
            "repository": "repository",
            "reposu": "reposu",
            "paket deposu": "paket deposu",
            
            # Ubuntu/Debian
            "ubuntu": "Ubuntu",
            "debian": "Debian",
            "linux": "Linux",
            
            # Yaygın hatalar
            "kurulumu": "kurulumu",
            "kaldırma": "kaldırma",
            "güncelleme": "güncelleme",
            "yükleme": "yükleme",
            
            # Kısaltmalar
            "d e b": "deb",
            "d.e.b": "deb",
            "dıb": "deb",
            
            # Kelime parçalanmaları
            "anlat tım": "anlattım",
            "hazırla mıştım": "hazırlamıştım",
            "kullanıla bilir": "kullanılabilir",
            "edebilir siniz": "edebilirsiniz",
        }
    
    def _load_tech_terms(self) -> Dict[str, str]:
        """
        Teknik terimlerin doğru yazılışları
        Büyük/küçük harf duyarlı
        
        Returns:
            {aranacak_pattern: doğru_yazılış}
        """
        return {
            # Komutlar (küçük harf)
            r'\bapt\b': 'apt',
            r'\bdpkg\b': 'dpkg',
            r'\bsudo\b': 'sudo',
            r'\bapt-get\b': 'apt-get',
            r'\bapt-cache\b': 'apt-cache',
            
            # Programlar (büyük harf)
            r'\bAPT\b(?! komutu)': 'APT',  # "APT komutu" hariç
            r'\bDPKG\b(?! komutu)': 'DPKG',
            r'\bUbuntu\b': 'Ubuntu',
            r'\bDebian\b': 'Debian',
            r'\bLinux\b': 'Linux',
            
            # Dosya uzantıları
            r'\.deb\b': '.deb',
            r'deb dosyası': 'deb dosyası',
            r'deb paketi': 'deb paketi',
            
            # Teknik terimler
            r'\bpackage manager\b': 'package manager',
            r'\brepository\b': 'repository',
            r'\bdependency\b': 'dependency',
            r'\bdependencies\b': 'dependencies',
        }
    
    def correct_text(self, text: str) -> str:
        """
        Metni düzelt
        
        Args:
            text: Düzeltilecek metin
            
        Returns:
            Düzeltilmiş metin
        """
        original = text
        
        # 1. Basit kelime değiştirmeleri (case-insensitive)
        for wrong, correct in self.corrections.items():
            # Kelime sınırlarını kontrol et
            pattern = r'\b' + re.escape(wrong) + r'\b'
            text = re.sub(pattern, correct, text, flags=re.IGNORECASE)
        
        # 2. Teknik terimleri düzelt (case-sensitive)
        for pattern, replacement in self.tech_terms.items():
            text = re.sub(pattern, replacement, text)
        
        # 3. Özel kurallar
        text = self._apply_special_rules(text)
        
        # Log (sadece değişiklik varsa)
        if text != original:
            logger.debug(f"Düzeltme: '{original}' → '{text}'")
        
        return text
    
    def _apply_special_rules(self, text: str) -> str:
        """
        Özel düzeltme kuralları
        
        Args:
            text: Metin
            
        Returns:
            Düzeltilmiş metin
        """
        # "apt komutu" gibi ifadelerde apt küçük, APT büyük olmalı
        text = re.sub(r'\bapt komutu\b', 'apt komutu', text, flags=re.IGNORECASE)
        text = re.sub(r'\bdpkg komutu\b', 'dpkg komutu', text, flags=re.IGNORECASE)
        
        # "APT ile" → "APT ile" (büyük harf)
        text = re.sub(r'\bapt ile\b', 'APT ile', text, flags=re.IGNORECASE)
        text = re.sub(r'\bdpkg ile\b', 'DPKG ile', text, flags=re.IGNORECASE)
        
        # "apt vs dpkg" → "APT vs DPKG"
        text = re.sub(r'\bapt vs dpkg\b', 'APT vs DPKG', text, flags=re.IGNORECASE)
        
        # ".deb dosyası" → ".deb dosyası"
        text = re.sub(r'\.?deb dosyası', '.deb dosyası', text, flags=re.IGNORECASE)
        
        # Gereksiz boşlukları temizle
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def correct_subtitle_segments(self, segments: List) -> List:
        """
        Altyazı segmentlerinin tümünü düzelt
        
        Args:
            segments: SubtitleSegment listesi
            
        Returns:
            Düzeltilmiş segment listesi
        """
        corrected_count = 0
        
        for segment in segments:
            original_text = segment.text
            corrected_text = self.correct_text(original_text)
            
            if corrected_text != original_text:
                segment.text = corrected_text
                corrected_count += 1
        
        logger.info(f"✓ {corrected_count}/{len(segments)} segment düzeltildi")
        
        return segments
    
    def add_custom_correction(self, wrong: str, correct: str):
        """
        Özel düzeltme kuralı ekle
        
        Args:
            wrong: Yanlış yazılış
            correct: Doğru yazılış
        """
        self.corrections[wrong] = correct
        logger.info(f"Özel kural eklendi: '{wrong}' → '{correct}'")
    
    def load_custom_dictionary(self, dict_path: Path):
        """
        Özel sözlük dosyası yükle
        
        Format (her satırda):
        yanlış|doğru
        
        Args:
            dict_path: Sözlük dosyası yolu
        """
        if not dict_path.exists():
            logger.warning(f"Sözlük dosyası bulunamadı: {dict_path}")
            return
        
        try:
            with open(dict_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and '|' in line:
                        wrong, correct = line.split('|', 1)
                        self.corrections[wrong.strip()] = correct.strip()
            
            logger.info(f"✓ Özel sözlük yüklendi: {dict_path}")
            
        except Exception as e:
            logger.error(f"Sözlük yükleme hatası: {e}")


# Test kodu
if __name__ == "__main__":
    corrector = SubtitleCorrector()
    
    # Test metinleri
    test_texts = [
        "apt paket yönütücüsü kullanarak kurulum yapabilirsiniz",
        "dpkg ile deb dosyası kurulumu",
        "ubuntu sisteminde apt komutu",
        "APT ve DPKG arasındaki fark",
        "paket yöneticesi ile bağımlılık çözümü"
    ]
    
    print("🔧 Altyazı Düzeltme Testleri:\n")
    for text in test_texts:
        corrected = corrector.correct_text(text)
        print(f"Önce : {text}")
        print(f"Sonra: {corrected}")
        print()
