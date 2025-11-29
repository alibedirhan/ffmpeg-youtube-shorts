# 📝 Değişiklik Günlüğü

Bu dosya, LinuxShorts Generator Pro'daki tüm önemli değişiklikleri içerir.

Format [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) standardına uygundur.

---

## [2.0.0] - 2024-11-29

### 🎉 Büyük Güncelleme - Modern GUI

Bu sürüm, uygulamanın tamamen yeniden tasarlanmış halidir.

### ✨ Eklenen
- **Modern GUI** - CustomTkinter ile tamamen yeni arayüz
- **Sidebar Navigasyon** - 7 sayfa (Ana Sayfa, Video Düzenle, Akıllı Analiz, Altyazı, Thumbnail, SEO, Export)
- **Gerçek Zamanlı Önizleme** - Canvas tabanlı video preview
- **Fare Sürükleme** - Video pozisyonunu fare ile ayarlama
- **Hassas Zoom** - Scroll ile %1'lik adımlarla zoom in/out
- **Akıllı Sığdırma** - Sığdır / Doldur / Ortala butonları
- **Arka Plan Modları** - Blur, Siyah, Özel Renk seçenekleri
- **Akıllı Analiz** - Hook algılama, sessizlik tespiti, sahne değişikliği
- **"En İyi Kesiti Kullan"** - Analiz sonuçlarını otomatik uygulama
- **Altyazı Oluşturma** - Whisper AI ile Türkçe altyazı
- **Zaman Aralığı Filtresi** - Sadece seçilen bölüm için altyazı
- **Altyazı Stili** - Font boyutu (8-48px), renk, pozisyon
- **SRT Export** - Altyazıyı dosyaya kaydetme
- **Thumbnail Oluşturucu** - En iyi frame bulma, efektler
- **SEO & Hashtag** - Akıllı öneriler, altyazı transcript kullanımı
- **Export Ayarları** - CRF, preset, çıktı dizini seçimi
- **Altyazı Gömme** - Burn-in subtitle desteği
- **Slider ↔ Entry Senkronizasyonu** - Zaman değerleri senkronize

### 🔄 Değiştirilen
- Video boyutlandırma mantığı tamamen yeniden yazıldı
- %100 zoom artık "fit to canvas" anlamına geliyor
- FFmpeg filter_complex ifadeleri optimize edildi
- Tüm widget'lar ModernCard, ModernButton, ModernSlider kullanıyor

### 🐛 Düzeltilen
- Export sırasında `str/int` tip hatası
- Thumbnail `num_frames` parametre hatası
- Lambda scope hataları (6 yer)
- Font callback hataları
- Duplicate `_find_best_frames` fonksiyonu
- Video çok küçük görünme sorunu

### 🗑️ Kaldırılan
- Eski tab-based GUI
- Kullanılmayan modüller

---

## [1.0.0] - 2024-11-01

### ✨ İlk Sürüm

- Temel video düzenleme
- FFmpeg entegrasyonu
- Basit GUI
- Altyazı desteği (temel)

---

## Gelecek Planlar

### [2.1.0] - Planlanan
- [ ] Video oynatma (play/pause)
- [ ] Gerçek progress bar (FFmpeg çıktısından)
- [ ] Çoklu segment desteği
- [ ] Batch processing

### [2.2.0] - Planlanan
- [ ] Watermark ekleme
- [ ] Aspect ratio seçenekleri (1:1, 4:5)
- [ ] Müzik ekleme
- [ ] Preset kaydet/yükle

---

## Sürüm Notları

### Semantic Versioning

Bu proje [Semantic Versioning](https://semver.org/) kullanır:

- **MAJOR**: Geriye uyumsuz API değişiklikleri
- **MINOR**: Geriye uyumlu yeni özellikler
- **PATCH**: Geriye uyumlu hata düzeltmeleri

### Sürüm Geçmişi

| Sürüm | Tarih | Notlar |
|-------|-------|--------|
| 2.0.0 | 2024-11-29 | Modern GUI, tam yeniden yazım |
| 1.0.0 | 2024-11-01 | İlk sürüm |
