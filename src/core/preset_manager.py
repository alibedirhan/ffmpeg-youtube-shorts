"""
LinuxShorts Generator - Preset Manager
Hazır video kesitleri yönetimi
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class PresetItem:
    """Tek bir preset öğesi"""
    name: str
    start_time: str  # HH:MM:SS formatında
    duration: str    # HH:MM:SS veya saniye
    description: str
    category: str = "Genel"
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> dict:
        """Dictionary'ye çevir"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PresetItem':
        """Dictionary'den oluştur"""
        return cls(**data)


class PresetManager:
    """Preset yönetim sınıfı"""
    
    def __init__(self, presets_dir: Path):
        """
        Args:
            presets_dir: Preset dosyalarının bulunduğu dizin
        """
        self.presets_dir = presets_dir
        self.presets_dir.mkdir(parents=True, exist_ok=True)
        self.presets: Dict[str, List[PresetItem]] = {}
        self._load_all_presets()
    
    def _load_all_presets(self) -> None:
        """Tüm preset dosyalarını yükler"""
        for preset_file in self.presets_dir.glob("*.json"):
            self.load_preset_file(preset_file)
    
    def load_preset_file(self, file_path: Path) -> bool:
        """
        Belirli bir preset dosyasını yükler
        
        Args:
            file_path: Preset JSON dosyası
            
        Returns:
            Başarılı ise True
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            preset_name = data.get('preset_name', file_path.stem)
            items = [PresetItem.from_dict(item) for item in data.get('items', [])]
            
            self.presets[preset_name] = items
            return True
            
        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            print(f"Preset yükleme hatası ({file_path}): {e}")
            return False
    
    def save_preset(
        self,
        preset_name: str,
        items: List[PresetItem],
        overwrite: bool = False
    ) -> bool:
        """
        Preset'i dosyaya kaydeder
        
        Args:
            preset_name: Preset adı
            items: Preset öğeleri
            overwrite: Üzerine yazılsın mı
            
        Returns:
            Başarılı ise True
        """
        file_path = self.presets_dir / f"{preset_name}.json"
        
        if file_path.exists() and not overwrite:
            print(f"Preset zaten mevcut: {preset_name}")
            return False
        
        data = {
            "preset_name": preset_name,
            "version": "1.0",
            "items": [item.to_dict() for item in items]
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.presets[preset_name] = items
            return True
            
        except Exception as e:
            print(f"Preset kaydetme hatası: {e}")
            return False
    
    def get_preset(self, preset_name: str) -> Optional[List[PresetItem]]:
        """
        Preset'i getirir
        
        Args:
            preset_name: Preset adı
            
        Returns:
            Preset öğeleri veya None
        """
        return self.presets.get(preset_name)
    
    def get_all_preset_names(self) -> List[str]:
        """Tüm preset isimlerini döndürür"""
        return list(self.presets.keys())
    
    def get_presets_by_category(self, category: str) -> Dict[str, List[PresetItem]]:
        """
        Kategoriye göre preset'leri filtreler
        
        Args:
            category: Kategori adı
            
        Returns:
            Filtrelenmiş preset dictionary
        """
        filtered = {}
        for preset_name, items in self.presets.items():
            category_items = [item for item in items if item.category == category]
            if category_items:
                filtered[preset_name] = category_items
        return filtered
    
    def search_presets(self, query: str) -> Dict[str, List[PresetItem]]:
        """
        Preset'lerde arama yapar
        
        Args:
            query: Arama kelimesi
            
        Returns:
            Eşleşen preset'ler
        """
        query = query.lower()
        results = {}
        
        for preset_name, items in self.presets.items():
            matching_items = [
                item for item in items
                if query in item.name.lower() or 
                   query in item.description.lower() or
                   any(query in tag.lower() for tag in item.tags)
            ]
            if matching_items:
                results[preset_name] = matching_items
        
        return results
    
    def delete_preset(self, preset_name: str) -> bool:
        """
        Preset'i siler
        
        Args:
            preset_name: Silinecek preset adı
            
        Returns:
            Başarılı ise True
        """
        file_path = self.presets_dir / f"{preset_name}.json"
        
        try:
            if file_path.exists():
                file_path.unlink()
            
            if preset_name in self.presets:
                del self.presets[preset_name]
            
            return True
            
        except Exception as e:
            print(f"Preset silme hatası: {e}")
            return False
    
    def create_example_preset(self) -> None:
        """Örnek preset oluşturur (ilk kullanım için)"""
        example_items = [
            PresetItem(
                name="APT vs DPKG Farkı",
                start_time="00:02:32",
                duration="00:01:11",
                description="APT ve DPKG arasındaki temel farklar",
                category="Linux Paket Yönetimi",
                tags=["apt", "dpkg", "paket-yönetimi"]
            ),
            PresetItem(
                name="Bağımlılık Çözümü",
                start_time="00:12:08",
                duration="00:00:47",
                description="Paket bağımlılıklarını çözme",
                category="Linux Paket Yönetimi",
                tags=["bağımlılık", "dependencies"]
            ),
            PresetItem(
                name="Asla Silmemeniz Gereken Paketler",
                start_time="00:14:25",
                duration="00:00:55",
                description="Kritik sistem paketleri",
                category="Linux Paket Yönetimi",
                tags=["sistem", "kritik", "dikkat"]
            ),
        ]
        
        self.save_preset("dpkg_video", example_items, overwrite=True)


# Test kodu
if __name__ == "__main__":
    from pathlib import Path
    
    # Test için geçici dizin
    test_dir = Path("/tmp/presets_test")
    test_dir.mkdir(exist_ok=True)
    
    manager = PresetManager(test_dir)
    
    # Örnek preset oluştur
    manager.create_example_preset()
    
    # Preset'leri listele
    print("📋 Mevcut Preset'ler:")
    for name in manager.get_all_preset_names():
        items = manager.get_preset(name)
        print(f"\n  {name}: {len(items)} öğe")
        for item in items:
            print(f"    - {item.name} ({item.start_time})")
    
    print("\n✅ Preset manager test başarılı!")
