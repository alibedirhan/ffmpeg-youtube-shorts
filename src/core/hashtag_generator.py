"""
LinuxShorts Generator - Hashtag Generator
Akıllı hashtag ve açıklama üretimi
"""

from pathlib import Path
from typing import List, Dict, Set
import re

from utils.logger import get_logger

logger = get_logger("LinuxShorts.Hashtag")


class HashtagGenerator:
    """Hashtag ve açıklama üretici"""
    
    def __init__(self):
        """Hashtag generator başlatıcı"""
        self.category_hashtags = self._load_category_hashtags()
        self.trending_topics = self._load_trending_topics()
        logger.info("Hashtag Generator başlatıldı")
    
    def _load_category_hashtags(self) -> Dict[str, List[str]]:
        """Kategori bazlı hashtag'leri yükler"""
        return {
            "Linux Paket Yönetimi": [
                "#Linux", "#Ubuntu", "#Debian", "#PackageManagement",
                "#APT", "#DPKG", "#LinuxTutorial", "#TürkçeLinux"
            ],
            "Terminal Komutları": [
                "#Linux", "#Terminal", "#Bash", "#CommandLine",
                "#LinuxCommands", "#BashScripting", "#TerminalTips"
            ],
            "Sistem Yönetimi": [
                "#Linux", "#SystemAdmin", "#DevOps", "#LinuxAdmin",
                "#ServerManagement", "#LinuxTips", "#SysAdmin"
            ],
            "Genel": [
                "#Linux", "#OpenSource", "#Technology", "#Tech",
                "#LinuxTutorial", "#LearnLinux", "#TürkçeLinux"
            ]
        }
    
    def _load_trending_topics(self) -> Dict[str, float]:
        """
        Trend konuları yükler (simüle edilmiş)
        Gerçek uygulamada YouTube API'den çekilebilir
        """
        return {
            "BashScripting": 125,  # Trend artış %
            "LinuxSecurity": 89,
            "TerminalTips": 56,
            "DockerTutorial": 45,
            "KubernetesTutorial": 38,
            "SystemdTips": 28
        }
    
    def generate_hashtags(
        self,
        category: str = "Genel",
        custom_keywords: List[str] = None,
        max_hashtags: int = 15
    ) -> List[str]:
        """
        Hashtag'leri üretir
        
        Args:
            category: Video kategorisi
            custom_keywords: Kullanıcı tanımlı anahtar kelimeler
            max_hashtags: Maksimum hashtag sayısı
            
        Returns:
            Hashtag listesi
        """
        logger.info(f"Hashtag'ler üretiliyor: kategori={category}")
        
        hashtags: Set[str] = set()
        
        # 1. Kategori hashtag'leri ekle
        category_tags = self.category_hashtags.get(category, self.category_hashtags["Genel"])
        hashtags.update(category_tags)
        
        # 2. Custom keyword'lerden hashtag'ler oluştur
        if custom_keywords:
            for keyword in custom_keywords:
                # Kelimedeki boşlukları kaldır, PascalCase yap
                tag = self._to_hashtag(keyword)
                hashtags.add(f"#{tag}")
        
        # 3. Trend hashtag'leri ekle (ilk 3)
        trend_tags = sorted(
            self.trending_topics.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        for tag, _ in trend_tags:
            hashtags.add(f"#{tag}")
        
        # 4. Genel popüler hashtag'ler
        popular = [
            "#Tutorial", "#HowTo", "#Tips", "#Tricks",
            "#Education", "#Learning", "#Tech", "#Programming"
        ]
        hashtags.update(popular[:5])
        
        # Listeye çevir ve sınırla
        result = list(hashtags)[:max_hashtags]
        
        logger.info(f"✓ {len(result)} hashtag oluşturuldu")
        return result
    
    def generate_description(
        self,
        video_title: str,
        category: str,
        hashtags: List[str],
        preset_name: str = None
    ) -> str:
        """
        Video açıklaması oluşturur
        
        Args:
            video_title: Video başlığı
            category: Kategori
            hashtags: Hashtag listesi
            preset_name: Preset adı (varsa)
            
        Returns:
            Açıklama metni
        """
        logger.info("Video açıklaması oluşturuluyor...")
        
        description_parts = []
        
        # 1. Ana açıklama
        description_parts.append(f"🎬 {video_title}")
        description_parts.append("")
        
        # 2. İçerik özeti
        if preset_name:
            description_parts.append(f"Bu videoda '{preset_name}' konusunu işliyoruz.")
        else:
            description_parts.append(f"Bu videoda {category.lower()} hakkında bilgi veriyoruz.")
        
        description_parts.append("")
        
        # 3. CTA (Call to Action)
        description_parts.append("👍 Beğenmeyi ve abone olmayı unutmayın!")
        description_parts.append("🔔 Bildirimleri açın, yeni videolardan haberdar olun!")
        description_parts.append("💬 Yorumlarda görüşlerinizi paylaşın!")
        description_parts.append("")
        
        # 4. Hashtag'ler
        description_parts.append("📌 Etiketler:")
        description_parts.append(" ".join(hashtags))
        description_parts.append("")
        
        # 5. İletişim
        description_parts.append("━━━━━━━━━━━━━━━━━━━━")
        description_parts.append("📺 Kanal: @alibedirhan.")
        description_parts.append("🔗 GitHub: github.com/alibedirhan")
        description_parts.append("━━━━━━━━━━━━━━━━━━━━")
        description_parts.append("")
        
        # 6. Disclaimer
        description_parts.append("#Shorts #LinuxTutorial #TürkçeLinux")
        
        description = "\n".join(description_parts)
        
        logger.info("✓ Açıklama oluşturuldu")
        logger.debug(f"Açıklama uzunluğu: {len(description)} karakter")
        
        return description
    
    def get_trending_summary(self) -> str:
        """
        Trend özeti döndürür
        
        Returns:
            Formatlanmış trend metni
        """
        lines = ["🔥 Bu Hafta Trend Konular:\n"]
        
        trends = sorted(
            self.trending_topics.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for i, (topic, change) in enumerate(trends[:5], 1):
            emoji = "🔥" if change > 100 else "📈"
            lines.append(f"{i}. #{topic}  {emoji} +{change}%")
        
        return "\n".join(lines)
    
    def _to_hashtag(self, text: str) -> str:
        """
        Metni hashtag formatına çevirir
        
        Args:
            text: Kaynak metin
            
        Returns:
            Hashtag formatı (PascalCase, boşluksuz)
        """
        # Türkçe karakterleri dönüştür
        replacements = {
            'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
            'Ç': 'C', 'Ğ': 'G', 'İ': 'I', 'Ö': 'O', 'Ş': 'S', 'Ü': 'U'
        }
        
        for tr_char, en_char in replacements.items():
            text = text.replace(tr_char, en_char)
        
        # Kelimeleri ayır ve PascalCase yap
        words = re.findall(r'\w+', text)
        pascal = ''.join(word.capitalize() for word in words)
        
        return pascal
    
    def suggest_title(
        self,
        preset_name: str,
        category: str
    ) -> str:
        """
        Video başlığı önerir
        
        Args:
            preset_name: Preset adı
            category: Kategori
            
        Returns:
            Önerilen başlık
        """
        # Başlık şablonları
        templates = [
            f"{preset_name} | Linux Dersleri 🐧",
            f"{preset_name} Nasıl Yapılır? | Linux Tutorial",
            f"Linux'ta {preset_name} - Hızlı Rehber ⚡",
            f"{preset_name} | {category} #Shorts",
            f"💻 {preset_name} | Linux Tips & Tricks"
        ]
        
        # İlkini döndür (gelecekte AI ile seçilebilir)
        return templates[0]


# Test kodu
if __name__ == "__main__":
    gen = HashtagGenerator()
    
    print("✅ Hashtag Generator hazır!\n")
    
    # Test hashtag generation
    print("📌 Örnek Hashtag'ler:")
    tags = gen.generate_hashtags(
        category="Linux Paket Yönetimi",
        custom_keywords=["DPKG", "Paket Kurulumu"]
    )
    print(" ".join(tags))
    
    print("\n" + "="*50)
    
    # Test description
    print("\n📝 Örnek Açıklama:")
    desc = gen.generate_description(
        video_title="DPKG ile Paket Yönetimi",
        category="Linux Paket Yönetimi",
        hashtags=tags,
        preset_name="APT vs DPKG Farkı"
    )
    print(desc)
    
    print("\n" + "="*50)
    
    # Test trending
    print("\n" + gen.get_trending_summary())
