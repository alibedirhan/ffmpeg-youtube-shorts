"""
LinuxShorts Pro - SEO Generator
YouTube Shorts için SEO önerileri: başlık, açıklama, hashtag
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from collections import Counter

from utils.logger import get_logger

logger = get_logger("LinuxShorts.SEO")


# Popüler YouTube Shorts kategorileri ve anahtar kelimeler
CATEGORY_KEYWORDS = {
    "teknoloji": ["linux", "terminal", "kod", "programlama", "yazılım", "ubuntu", "komut", 
                  "bilgisayar", "geliştirici", "developer", "coding", "tech"],
    "eğitim": ["nasıl", "öğren", "tutorial", "rehber", "ipucu", "trick", "tip", 
               "başlangıç", "kolay", "hızlı", "adım adım"],
    "eğlence": ["komik", "eğlenceli", "şaşırtıcı", "inanılmaz", "muhteşem"],
    "günlük": ["vlog", "günlük", "hayat", "rutin", "gün"]
}

# Viral başlık kalıpları
VIRAL_PATTERNS = [
    "Bu {konu} Hakkında Bilmediğiniz {sayı} Şey",
    "{sayı} Saniyede {konu} Öğren",
    "{konu} Yaparken BUNU Yapma!",
    "Hiç Kimsenin Bilmediği {konu} Sırrı",
    "{konu} için EN İYİ {sayı} İpucu",
    "SADECE {sayı} Komutla {konu}",
    "{konu} Nasıl Yapılır? (KOLAY)",
    "Bu {konu} Trick'i Hayatınızı Değiştirecek",
]

# Popüler hashtagler
POPULAR_HASHTAGS = {
    "genel": ["#shorts", "#viral", "#fyp", "#trending", "#keşfet"],
    "teknoloji": ["#linux", "#ubuntu", "#terminal", "#coding", "#programming", 
                  "#developer", "#tech", "#yazılım", "#kod", "#bilişim"],
    "eğitim": ["#öğren", "#tutorial", "#howto", "#tips", "#tricks", "#eğitim"],
    "türkçe": ["#türkiye", "#türkçe", "#tr"]
}


@dataclass
class SEOSuggestion:
    """SEO önerisi"""
    title: str
    description: str
    hashtags: List[str]
    keywords: List[str]
    score: float = 0.0
    tips: List[str] = field(default_factory=list)


@dataclass
class VideoMetadata:
    """Video meta verisi"""
    filename: str = ""
    duration: float = 0.0
    transcript: str = ""
    detected_topics: List[str] = field(default_factory=list)
    language: str = "tr"


class SEOGenerator:
    """YouTube Shorts için SEO önerileri oluştur"""
    
    def __init__(self):
        self.metadata: Optional[VideoMetadata] = None
        self.suggestions: List[SEOSuggestion] = []
    
    def analyze_content(self, transcript: str = "", filename: str = "", 
                       duration: float = 0.0) -> VideoMetadata:
        """İçeriği analiz et"""
        self.metadata = VideoMetadata(
            filename=filename,
            duration=duration,
            transcript=transcript.lower()
        )
        
        # Konuları tespit et
        self.metadata.detected_topics = self._detect_topics(transcript)
        
        logger.info(f"İçerik analiz edildi: {len(self.metadata.detected_topics)} konu tespit edildi")
        return self.metadata
    
    def _detect_topics(self, text: str) -> List[str]:
        """Metinden konuları tespit et"""
        text_lower = text.lower()
        topics = []
        
        for category, keywords in CATEGORY_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches >= 2:
                topics.append(category)
        
        return topics if topics else ["genel"]
    
    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Metinden anahtar kelimeler çıkar"""
        # Türkçe stop words
        stop_words = {"bir", "ve", "bu", "için", "ile", "de", "da", "ne", "var", 
                     "ben", "sen", "o", "biz", "siz", "onlar", "çok", "daha",
                     "olan", "olarak", "gibi", "kadar", "sonra", "önce", "ama"}
        
        # Kelimeleri ayır
        words = re.findall(r'\b[a-zA-ZğüşıöçĞÜŞİÖÇ]{3,}\b', text.lower())
        
        # Stop words'leri çıkar
        words = [w for w in words if w not in stop_words]
        
        # En sık geçenleri bul
        counter = Counter(words)
        return [word for word, _ in counter.most_common(max_keywords)]
    
    def generate_titles(self, topic: str = "", count: int = 5) -> List[str]:
        """Başlık önerileri oluştur"""
        titles = []
        
        if not topic and self.metadata:
            topic = self.metadata.detected_topics[0] if self.metadata.detected_topics else "Linux"
        
        topic = topic.capitalize()
        
        for pattern in VIRAL_PATTERNS[:count]:
            title = pattern.format(
                konu=topic,
                sayı=str(3 + len(titles) % 5)  # 3-7 arası sayı
            )
            titles.append(title)
        
        # Özel başlıklar
        if self.metadata and self.metadata.transcript:
            keywords = self._extract_keywords(self.metadata.transcript, 3)
            if keywords:
                titles.append(f"{keywords[0].capitalize()} Hakkında Bilmeniz Gerekenler")
                titles.append(f"{keywords[0].capitalize()} - Hızlı Rehber")
        
        return titles[:count]
    
    def generate_descriptions(self, title: str = "", count: int = 3) -> List[str]:
        """Açıklama önerileri oluştur"""
        descriptions = []
        
        topics = self.metadata.detected_topics if self.metadata else ["genel"]
        
        templates = [
            "🎯 Bu videoda {konu} hakkında önemli bilgiler paylaşıyorum.\n\n"
            "👍 Beğenmeyi ve abone olmayı unutma!\n\n"
            "📌 Daha fazla içerik için kanalıma göz at.\n\n"
            "{hashtags}",
            
            "💡 {konu} ile ilgili bilmeniz gereken her şey bu videoda!\n\n"
            "🔔 Bildirimleri aç, yeni videoları kaçırma!\n\n"
            "{hashtags}",
            
            "🚀 Hızlı ve pratik {konu} rehberi.\n\n"
            "📺 Diğer videolarıma da göz atmayı unutma!\n\n"
            "💬 Sorularınızı yorumlara yazın.\n\n"
            "{hashtags}"
        ]
        
        hashtags = self.generate_hashtags(topics)
        hashtag_str = " ".join(hashtags[:10])
        
        for template in templates[:count]:
            desc = template.format(
                konu=topics[0] if topics else "bu konu",
                hashtags=hashtag_str
            )
            descriptions.append(desc)
        
        return descriptions
    
    def generate_hashtags(self, topics: List[str] = None, max_count: int = 15, custom_topic: str = "") -> List[str]:
        """Hashtag önerileri oluştur"""
        if topics is None:
            topics = self.metadata.detected_topics if self.metadata else ["genel"]
        
        hashtags = set()
        
        # Custom topic varsa, ondan hashtag oluştur
        if custom_topic:
            # Girilen kelimeyi hashtag'e çevir
            clean_topic = custom_topic.strip().lower()
            hashtags.add(f"#{clean_topic}")
            
            # İlgili hashtagler
            topic_related = {
                "linux": ["#linux", "#ubuntu", "#debian", "#terminal", "#opensource", "#linuxtutorial", "#linuxtips", "#commandline"],
                "terminal": ["#terminal", "#bash", "#commandline", "#cli", "#shell", "#linuxterminal"],
                "ubuntu": ["#ubuntu", "#linux", "#debian", "#apt", "#gnome", "#ubuntutips"],
                "python": ["#python", "#coding", "#programming", "#pythontips", "#developer"],
                "kod": ["#coding", "#programming", "#developer", "#yazılım", "#software"],
                "dpkg": ["#dpkg", "#debian", "#linux", "#packagemanagement", "#apt"],
                "apt": ["#apt", "#aptget", "#linux", "#ubuntu", "#debian", "#packagemanager"],
                "snap": ["#snap", "#snapcraft", "#ubuntu", "#linux", "#flatpak"],
                "git": ["#git", "#github", "#gitlab", "#versioncontrol", "#developer"],
            }
            
            # Eşleşen hashtagleri ekle
            for keyword, related in topic_related.items():
                if keyword in clean_topic:
                    hashtags.update(related[:5])
        
        # Teknoloji hashtagleri
        hashtags.update(POPULAR_HASHTAGS.get("teknoloji", [])[:5])
        
        # Genel hashtagler
        hashtags.update(["#shorts", "#tutorial", "#howto"])
        
        # Türkçe hashtagler
        hashtags.update(["#türkçe", "#türkiye"])
        
        return list(hashtags)[:max_count]
    
    def generate_full_suggestion(self, topic: str = "") -> SEOSuggestion:
        """Tam SEO önerisi oluştur"""
        original_topic = topic  # Kullanıcının girdiği orijinal konu
        
        if not topic and self.metadata:
            topic = self.metadata.detected_topics[0] if self.metadata.detected_topics else "genel"
        
        titles = self.generate_titles(topic, 1)
        descriptions = self.generate_descriptions(titles[0] if titles else "", 1)
        hashtags = self.generate_hashtags([topic], custom_topic=original_topic)
        keywords = self._extract_keywords(
            self.metadata.transcript if self.metadata else "", 10
        )
        
        # Skor hesapla
        score = 50.0
        tips = []
        
        # Başlık uzunluğu (ideal: 40-60 karakter)
        if titles:
            title_len = len(titles[0])
            if 40 <= title_len <= 60:
                score += 15
            elif title_len > 70:
                tips.append("⚠️ Başlık çok uzun, 60 karakterin altında tut")
            elif title_len < 30:
                tips.append("⚠️ Başlık çok kısa, daha açıklayıcı yap")
        
        # Hashtag sayısı
        if 5 <= len(hashtags) <= 10:
            score += 10
        else:
            tips.append("💡 5-10 arası hashtag kullan")
        
        # Emoji kullanımı
        if descriptions and any(c for c in descriptions[0] if ord(c) > 0x1F600):
            score += 5
        else:
            tips.append("💡 Açıklamada emoji kullan")
        
        # CTA (Call to Action)
        if descriptions and ("abone" in descriptions[0].lower() or "beğen" in descriptions[0].lower()):
            score += 10
        else:
            tips.append("💡 Abone ol/Beğen çağrısı ekle")
        
        # Konu tespiti başarılı mı
        if self.metadata and len(self.metadata.detected_topics) > 0:
            score += 10
        
        return SEOSuggestion(
            title=titles[0] if titles else "",
            description=descriptions[0] if descriptions else "",
            hashtags=hashtags,
            keywords=keywords,
            score=min(100, score),
            tips=tips
        )
    
    def generate_multiple_suggestions(self, count: int = 3) -> List[SEOSuggestion]:
        """Birden fazla SEO önerisi"""
        self.suggestions = []
        
        topics = self.metadata.detected_topics if self.metadata else ["genel"]
        
        for i in range(count):
            topic = topics[i % len(topics)]
            suggestion = self.generate_full_suggestion(topic)
            
            # Başlık varyasyonları
            titles = self.generate_titles(topic, count)
            if i < len(titles):
                suggestion.title = titles[i]
            
            self.suggestions.append(suggestion)
        
        return self.suggestions
    
    def get_optimization_tips(self) -> List[str]:
        """Genel optimizasyon ipuçları"""
        tips = [
            "📱 İlk 3 saniye çok önemli - dikkat çekici başla",
            "🎯 Tek bir konuya odaklan",
            "⏱️ 30-45 saniye ideal Short süresi",
            "📝 Açıklamada ilk 2 satır görünür, önemli bilgiyi başa yaz",
            "🔄 Düzenli paylaşım algoritma için önemli",
            "📊 En iyi saatler: 12:00-14:00 ve 19:00-22:00",
            "🏷️ #shorts hashtag'i zorunlu",
            "🎵 Trending müzik kullanımı erişimi artırır",
            "💬 Yorumlara cevap ver, etkileşim önemli",
            "📈 İlk 1 saat çok kritik - hemen paylaş"
        ]
        return tips
    
    def analyze_title(self, title: str) -> Dict:
        """Başlık analizi"""
        analysis = {
            "length": len(title),
            "word_count": len(title.split()),
            "has_emoji": any(ord(c) > 0x1F600 for c in title),
            "has_numbers": any(c.isdigit() for c in title),
            "has_uppercase": any(c.isupper() for c in title),
            "score": 50,
            "suggestions": []
        }
        
        # Uzunluk skoru
        if 40 <= analysis["length"] <= 60:
            analysis["score"] += 20
        elif analysis["length"] > 70:
            analysis["suggestions"].append("Başlık çok uzun")
        elif analysis["length"] < 25:
            analysis["suggestions"].append("Başlık çok kısa")
        
        # Sayı varsa bonus
        if analysis["has_numbers"]:
            analysis["score"] += 10
        else:
            analysis["suggestions"].append("Başlığa sayı ekle (örn: '5 İpucu')")
        
        # Büyük harf varsa
        if analysis["has_uppercase"]:
            analysis["score"] += 5
        
        # Power words kontrolü
        power_words = ["nasıl", "neden", "en iyi", "hızlı", "kolay", "şimdi", 
                      "ücretsiz", "yeni", "sır", "muhteşem"]
        for word in power_words:
            if word in title.lower():
                analysis["score"] += 5
                break
        
        analysis["score"] = min(100, analysis["score"])
        return analysis
