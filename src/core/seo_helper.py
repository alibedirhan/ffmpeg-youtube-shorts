"""
LinuxShorts Pro - SEO Helper Module
YouTube Shorts için SEO önerileri, başlık ve açıklama üretimi
"""

import re
import random
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from utils.logger import get_logger

logger = get_logger("LinuxShorts.SEOHelper")


@dataclass
class SEOSuggestion:
    """SEO önerisi"""
    titles: list = field(default_factory=list)
    descriptions: list = field(default_factory=list)
    hashtags: list = field(default_factory=list)
    tags: list = field(default_factory=list)
    best_upload_times: list = field(default_factory=list)
    tips: list = field(default_factory=list)


class SEOHelper:
    """YouTube Shorts SEO yardımcısı"""
    
    TITLE_PATTERNS = [
        "{topic} Hakkında Bilmediğiniz {count} Şey 🤯",
        "{topic} - 1 Dakikada Öğren! ⚡",
        "Bu {topic} Trick'i Hayatınızı Değiştirecek 🔥",
        "{topic} Nasıl Yapılır? (Kolay Yöntem) ✅",
        "{count} Saniyede {topic} 🚀",
        "{topic} İpuçları - Bunu Deneyin! 💡",
        "Kimse Bilmiyor: {topic} Sırları 🤫",
        "{topic} Başlangıç Rehberi 📚",
        "Acemi Hatası: {topic} Yaparken Dikkat! ⚠️",
        "{topic} - Pro Gibi Kullan 😎",
    ]
    
    LINUX_HASHTAGS = [
        "#linux", "#ubuntu", "#terminal", "#opensource", "#coding",
        "#programming", "#developer", "#tech", "#linuxturkey", "#yazılım",
        "#teknoloji", "#bilişim", "#kodlama", "#sibergüvenlik",
        "#linuxtips", "#linuxtutorial", "#commandline", "#bash", "#shell"
    ]
    
    SHORTS_HASHTAGS = [
        "#shorts", "#youtubeshorts", "#short", "#viral", "#trending",
        "#fyp", "#foryou", "#keşfet", "#türkiye"
    ]
    
    BEST_UPLOAD_TIMES = [
        {"day": "Pazartesi", "times": ["12:00", "18:00", "21:00"], "reason": "Öğle molası ve akşam"},
        {"day": "Salı", "times": ["12:00", "17:00", "20:00"], "reason": "Hafta ortası aktif"},
        {"day": "Çarşamba", "times": ["12:00", "18:00", "21:00"], "reason": "Orta hafta"},
        {"day": "Perşembe", "times": ["12:00", "17:00", "21:00"], "reason": "Hafta sonu öncesi"},
        {"day": "Cuma", "times": ["12:00", "15:00", "20:00"], "reason": "Hafta sonu başlangıcı"},
        {"day": "Cumartesi", "times": ["10:00", "14:00", "20:00"], "reason": "Hafta sonu yoğun"},
        {"day": "Pazar", "times": ["10:00", "15:00", "19:00"], "reason": "Hafta sonu dinlenme"},
    ]
    
    DESCRIPTION_TEMPLATES = [
        """🔥 {title}

{summary}

📌 Bu videoda:
{points}

💬 Sorularınızı yorumlarda bekliyorum!

{hashtags}""",

        """{emoji} {title}

{summary}

⚡ İpucu: {tip}

👆 Beğen + Kaydet!

{hashtags}""",

        """💡 {title}

{summary}

📢 Abone ol, bildirimleri aç!

{hashtags}""",
    ]
    
    SEO_TIPS = [
        "📌 Başlığı 40 karakter altında tut",
        "🔥 İlk 3 saniye hook ile başla",
        "📱 Dikey video (9:16) kullan",
        "#️⃣ 3-5 hashtag yeterli",
        "⏰ 15-30 saniye ideal süre",
        "🎵 Trend müzik kullan",
        "💬 Yorum sormak engagement artırır",
        "🔄 İlk 1 saat kritik",
        "📊 Analytics'i takip et",
        "🎯 Niş odaklı içerik üret",
        "✍️ Altyazı ekle",
        "🖼️ Dikkat çekici thumbnail",
        "📝 Açıklamaya anahtar kelime ekle",
        "📈 Günde 1-3 Short ideal",
    ]
    
    def __init__(self):
        logger.info("SEOHelper başlatıldı")
    
    def generate_suggestions(
        self,
        topic: str = "",
        keywords: list = None,
        video_duration: float = 60,
        category: str = "linux"
    ) -> SEOSuggestion:
        """SEO önerileri oluştur"""
        suggestion = SEOSuggestion()
        
        if keywords is None:
            keywords = []
        
        suggestion.titles = self._generate_titles(topic, keywords)
        suggestion.descriptions = self._generate_descriptions(topic, keywords)
        suggestion.hashtags = self._generate_hashtags(topic, keywords, category)
        suggestion.tags = self._generate_tags(topic, keywords, category)
        suggestion.best_upload_times = self._get_best_upload_times()
        suggestion.tips = random.sample(self.SEO_TIPS, min(5, len(self.SEO_TIPS)))
        
        return suggestion
    
    def _generate_titles(self, topic: str, keywords: list) -> list:
        """Başlık önerileri"""
        titles = []
        
        if not topic:
            topic = "Linux"
        
        counts = ["3", "5", "7", "10"]
        
        for pattern in self.TITLE_PATTERNS[:6]:
            title = pattern.format(
                topic=topic,
                count=random.choice(counts),
                seconds=random.choice(["30", "45", "60"])
            )
            titles.append(title)
        
        for kw in keywords[:2]:
            titles.append(f"{kw} - Hızlı Rehber 🚀")
        
        return titles[:8]
    
    def _generate_descriptions(self, topic: str, keywords: list) -> list:
        """Açıklama önerileri"""
        descriptions = []
        
        if not topic:
            topic = "Linux"
        
        emojis = ["🔥", "💡", "⚡", "🚀", "✨"]
        tips = ["Her gün pratik yapın!", "Notlarınızı tutun.", "Deneye deneye öğrenin."]
        hashtags = " ".join(self._generate_hashtags(topic, keywords, "linux")[:5])
        
        for template in self.DESCRIPTION_TEMPLATES:
            desc = template.format(
                title=f"{topic} Rehberi",
                summary=f"Bu videoda {topic.lower()} hakkında bilmeniz gerekenleri öğreneceksiniz.",
                points="• Temel kavramlar\n• Pratik örnekler\n• Pro ipuçları",
                tip=random.choice(tips),
                emoji=random.choice(emojis),
                hashtags=hashtags
            )
            descriptions.append(desc)
        
        return descriptions
    
    def _generate_hashtags(self, topic: str, keywords: list, category: str) -> list:
        """Hashtag önerileri"""
        hashtags = ["#shorts", "#youtubeshorts"]
        
        if category == "linux":
            hashtags.extend(random.sample(self.LINUX_HASHTAGS, 5))
        
        if topic:
            clean_topic = re.sub(r'[^a-zA-ZğüşıöçĞÜŞİÖÇ0-9]', '', topic.lower())
            if clean_topic:
                hashtags.append(f"#{clean_topic}")
        
        for kw in keywords[:3]:
            clean_kw = re.sub(r'[^a-zA-ZğüşıöçĞÜŞİÖÇ0-9]', '', kw.lower())
            if clean_kw and f"#{clean_kw}" not in hashtags:
                hashtags.append(f"#{clean_kw}")
        
        hashtags.extend(["#keşfet", "#türkiye"])
        
        seen = set()
        unique = []
        for h in hashtags:
            if h.lower() not in seen:
                seen.add(h.lower())
                unique.append(h)
        
        return unique[:12]
    
    def _generate_tags(self, topic: str, keywords: list, category: str) -> list:
        """YouTube tag önerileri"""
        tags = ["shorts", "youtube shorts", "short video"]
        
        if category == "linux":
            tags.extend([
                "linux", "linux tutorial", "linux türkçe",
                "ubuntu", "terminal", "linux öğren"
            ])
        
        if topic:
            tags.append(topic.lower())
            tags.append(f"{topic.lower()} tutorial")
        
        for kw in keywords:
            if kw.lower() not in tags:
                tags.append(kw.lower())
        
        return tags[:20]
    
    def _get_best_upload_times(self) -> list:
        """En iyi yayın zamanları"""
        today = datetime.now().strftime("%A")
        day_map = {
            "Monday": "Pazartesi", "Tuesday": "Salı", "Wednesday": "Çarşamba",
            "Thursday": "Perşembe", "Friday": "Cuma", "Saturday": "Cumartesi",
            "Sunday": "Pazar"
        }
        
        today_tr = day_map.get(today, "Pazartesi")
        
        times = []
        for t in self.BEST_UPLOAD_TIMES:
            if t["day"] == today_tr:
                times.insert(0, {**t, "is_today": True})
            else:
                times.append({**t, "is_today": False})
        
        return times
    
    def analyze_title(self, title: str) -> dict:
        """Başlık analizi"""
        analysis = {
            "length": len(title),
            "has_emoji": bool(re.search(r'[\U0001F300-\U0001F9FF]', title)),
            "has_numbers": bool(re.search(r'\d', title)),
            "has_question": "?" in title,
            "is_caps_heavy": sum(1 for c in title if c.isupper()) > len(title) * 0.3,
            "score": 0,
            "suggestions": []
        }
        
        score = 50
        
        if 20 <= analysis["length"] <= 50:
            score += 15
        elif analysis["length"] < 20:
            analysis["suggestions"].append("Başlık biraz kısa")
        else:
            analysis["suggestions"].append("Başlık çok uzun, mobilde kesilecek")
            score -= 10
        
        if analysis["has_emoji"]:
            score += 10
        else:
            analysis["suggestions"].append("Emoji eklemek dikkat çeker 🔥")
        
        if analysis["has_numbers"]:
            score += 10
            
        if analysis["is_caps_heavy"]:
            score -= 15
            analysis["suggestions"].append("Çok fazla büyük harf")
        
        analysis["score"] = min(100, max(0, score))
        
        return analysis
    
    def analyze_description(self, description: str) -> dict:
        """Açıklama analizi"""
        analysis = {
            "length": len(description),
            "hashtag_count": len(re.findall(r'#\w+', description)),
            "has_cta": any(cta in description.lower() for cta in 
                         ["abone", "beğen", "yorum", "takip", "subscribe", "like"]),
            "has_emoji": bool(re.search(r'[\U0001F300-\U0001F9FF]', description)),
            "score": 0,
            "suggestions": []
        }
        
        score = 50
        
        if 100 <= analysis["length"] <= 500:
            score += 15
        elif analysis["length"] < 100:
            analysis["suggestions"].append("Açıklama biraz kısa")
        
        if 3 <= analysis["hashtag_count"] <= 8:
            score += 15
        elif analysis["hashtag_count"] > 10:
            analysis["suggestions"].append("Çok fazla hashtag")
            score -= 10
        
        if analysis["has_cta"]:
            score += 15
        else:
            analysis["suggestions"].append("Call-to-action ekleyin")
        
        if analysis["has_emoji"]:
            score += 5
        
        analysis["score"] = min(100, max(0, score))
        
        return analysis
