# 🎬 LinuxShorts Generator Pro v2.0

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Linux-orange.svg)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-red.svg)

**Yatay videolarınızı profesyonel YouTube Shorts'a dönüştürün!**

[Özellikler](#-özellikler) • [Kurulum](#-kurulum) • [Kullanım](#-kullanım) • [Ekran Görüntüleri](#-ekran-görüntüleri) • [Katkıda Bulunun](#-katkıda-bulunun)

</div>

---

## 📖 Hakkında

LinuxShorts Generator Pro, yatay (16:9) videolarınızı dikey (9:16) YouTube Shorts formatına dönüştürmek için tasarlanmış kapsamlı bir masaüstü uygulamasıdır. Modern GUI, akıllı analiz, otomatik altyazı oluşturma ve SEO önerileri ile içerik üreticilerin işini kolaylaştırır.

### 🎯 Neden LinuxShorts?

- ✅ **Tamamen Ücretsiz ve Açık Kaynak**
- ✅ **Yerel İşleme** - Videolarınız bilgisayarınızdan çıkmaz
- ✅ **Türkçe Arayüz** - Türk içerik üreticileri için optimize
- ✅ **Whisper AI Desteği** - Otomatik Türkçe altyazı
- ✅ **Akıllı Analiz** - En iyi kesitleri otomatik bulma

---

## ✨ Özellikler

### 🎥 Video Düzenleme
- **Gerçek Zamanlı Önizleme** - Değişiklikleri anında görün
- **Sürükle & Bırak** - Fare ile video pozisyonunu ayarlayın
- **Hassas Zoom** - Scroll ile %1'lik adımlarla zoom
- **Akıllı Sığdırma** - Sığdır / Doldur / Ortala butonları
- **Arka Plan Modları** - Blur, Siyah veya Özel Renk

### 🧠 Akıllı Analiz
- **Hook Algılama** - İzleyiciyi yakalayacak anları bulur
- **Sessizlik Tespiti** - Sessiz bölümleri otomatik algılar
- **Sahne Değişikliği** - Geçiş noktalarını tespit eder
- **En İyi Kesit Önerisi** - Skor bazlı öneri sistemi

### 📝 Otomatik Altyazı
- **Whisper AI** - OpenAI'nin ses tanıma modeli
- **Türkçe Desteği** - Türkçe konuşma tanıma
- **SRT Export** - Standart altyazı formatı
- **Stil Özelleştirme** - Font, renk, pozisyon ayarları

### 🖼️ Thumbnail Oluşturucu
- **Otomatik Frame Seçimi** - En iyi kareleri bulur
- **Efekt Uygulama** - Parlaklık, kontrast, doygunluk
- **Başlık Ekleme** - Özelleştirilebilir metin
- **1280x720 Export** - YouTube standart boyutu

### 📊 SEO & Hashtag
- **Akıllı Başlık Önerileri** - Konuya uygun başlıklar
- **Hashtag Üretici** - Viral hashtag önerileri
- **Açıklama Şablonları** - Hazır açıklama metinleri
- **Panoya Kopyalama** - Tek tıkla kopyala

### 🚀 Export
- **1080x1920 Çıktı** - YouTube Shorts standart çözünürlük
- **Altyazı Gömme** - Burn-in subtitle desteği
- **Kalite Ayarları** - CRF ve preset seçenekleri
- **Özel Çıktı Dizini** - İstediğiniz klasöre kaydedin

---

## 💻 Sistem Gereksinimleri

| Bileşen | Minimum | Önerilen |
|---------|---------|----------|
| **İşletim Sistemi** | Ubuntu 20.04+ / Debian 11+ | Ubuntu 22.04+ |
| **Python** | 3.10+ | 3.11+ |
| **RAM** | 4 GB | 8 GB+ |
| **Disk Alanı** | 5 GB | 10 GB+ |
| **GPU** | - | CUDA destekli (Whisper için) |

### Gerekli Paketler
- FFmpeg
- Python 3.10+
- Tkinter
- OpenCV
- Whisper AI (opsiyonel)

---

## 🚀 Kurulum

### Yöntem 1: Otomatik Kurulum (Önerilen)

```bash
# Repoyu klonlayın
git clone https://github.com/alibedirhan/ffmpeg-youtube-shorts.git
cd ffmpeg-youtube-shorts

# Kurulum scriptini çalıştırın
chmod +x install.sh
./install.sh

# Programı başlatın
./run.sh
```

### Yöntem 2: Manuel Kurulum

```bash
# Sistem paketlerini kurun
sudo apt update
sudo apt install -y ffmpeg python3 python3-pip python3-venv python3-tk fonts-dejavu-core

# Repoyu klonlayın
git clone https://github.com/alibedirhan/ffmpeg-youtube-shorts.git
cd ffmpeg-youtube-shorts

# Sanal ortam oluşturun
python3 -m venv venv
source venv/bin/activate

# Python paketlerini kurun
pip install --upgrade pip
pip install -r requirements.txt

# Programı başlatın
python3 main.py
```

### Yöntem 3: Pip ile Bağımlılıklar (Sanal Ortam Olmadan)

```bash
# Sistem paketleri
sudo apt install -y ffmpeg python3-tk

# Python paketleri (--break-system-packages gerekebilir)
pip install customtkinter pillow opencv-python numpy --break-system-packages

# Whisper (opsiyonel - büyük download)
pip install openai-whisper torch torchaudio --break-system-packages
```

---

## 📖 Kullanım

### Hızlı Başlangıç

1. **Video Yükle** - Ana sayfadan video seçin
2. **Düzenle** - Zoom, pozisyon ve arka plan ayarlayın
3. **Altyazı** - Otomatik altyazı oluşturun (opsiyonel)
4. **Export** - Shorts olarak kaydedin

### Detaylı Kullanım Kılavuzu

#### 🏠 Ana Sayfa
- `Video Seç` butonuna tıklayın
- Desteklenen formatlar: MP4, AVI, MKV, MOV, WEBM

#### 🎬 Video Düzenleme

| Kontrol | İşlev |
|---------|-------|
| **Fare Sürükleme** | Video pozisyonunu ayarla |
| **Scroll** | Zoom in/out (%1 adım) |
| **Sığdır** | Videoyu canvas'a sığdır |
| **Doldur** | Ekranı tamamen doldur |
| **Ortala** | Pozisyonu sıfırla |

**Zaman Aralığı:**
- Başlangıç: Video'nun başlangıç zamanı (00:01:30 formatı)
- Süre: Kesitin uzunluğu (saniye, max 60)
- Slider ile başlangıç zamanı senkronize çalışır

**Arka Plan Modları:**
- **Siyah**: Klasik siyah kenarlar
- **Blur**: Bulanık video arka planı (önerilen)
- **Renk**: Özel renk seçimi

#### 🧠 Akıllı Analiz
1. `Analizi Başlat` butonuna tıklayın
2. Analiz tamamlandığında önerilen kesitleri görün
3. `En İyi Kesiti Kullan` ile otomatik uygulayın

#### 📝 Altyazı Oluşturma

| Model | Hız | Doğruluk | Boyut |
|-------|-----|----------|-------|
| tiny | ⚡⚡⚡⚡ | ⭐ | 75 MB |
| base | ⚡⚡⚡ | ⭐⭐ | 150 MB |
| small | ⚡⚡ | ⭐⭐⭐ | 500 MB |
| medium | ⚡ | ⭐⭐⭐⭐ | 1.5 GB |
| large | 🐢 | ⭐⭐⭐⭐⭐ | 3 GB |

> ⚠️ İlk kullanımda model indirilir

#### 🖼️ Thumbnail
1. Zaman slider'ı ile kare seçin
2. `En İyi Frame'leri Bul` ile önerileri görün
3. Efektleri ayarlayın (parlaklık, kontrast, doygunluk)
4. `Thumbnail Kaydet` ile PNG/JPG olarak kaydedin

#### 🚀 Export
1. Video düzenleme ayarlarını yapın
2. `Altyazıyı Göm` seçeneğini işaretleyin (opsiyonel)
3. Çıktı dizinini seçin
4. `SHORT OLUŞTUR` butonuna tıklayın

**Çıktı:** `~/linuxshorts_output/video_short.mp4`

---

## 📁 Proje Yapısı

```
ffmpeg-youtube-shorts/
├── main.py                 # Ana giriş noktası
├── requirements.txt        # Python bağımlılıkları
├── install.sh              # Otomatik kurulum scripti
├── run.sh                  # Başlatma scripti
├── README.md               # Bu dosya
├── LICENSE                 # MIT Lisansı
├── CONTRIBUTING.md         # Katkı rehberi
├── CHANGELOG.md            # Değişiklik günlüğü
│
├── src/
│   ├── __init__.py
│   │
│   ├── core/               # İş mantığı modülleri
│   │   ├── ffmpeg_wrapper.py      # FFmpeg işlemleri
│   │   ├── subtitle_generator.py  # Whisper altyazı
│   │   ├── smart_analyzer.py      # Akıllı analiz
│   │   ├── thumbnail_generator.py # Thumbnail oluşturma
│   │   ├── seo_generator.py       # SEO önerileri
│   │   └── ...
│   │
│   ├── gui/                # Kullanıcı arayüzü
│   │   ├── main_window.py  # Ana pencere
│   │   └── ...
│   │
│   └── utils/              # Yardımcı modüller
│       ├── config.py       # Yapılandırma
│       └── logger.py       # Loglama
│
└── docs/                   # Ek dökümantasyon
    └── USAGE_GUIDE.md      # Detaylı kullanım kılavuzu
```

---

## ⌨️ Klavye Kısayolları

| Kısayol | İşlev |
|---------|-------|
| `Scroll Up` | Zoom In (%1) |
| `Scroll Down` | Zoom Out (%1) |
| `Enter` (Zaman entry'de) | Zamanı uygula |
| `Sol Fare + Sürükle` | Video pozisyonunu değiştir |

---

## 🐛 Sorun Giderme

### Sık Karşılaşılan Sorunlar

#### FFmpeg bulunamadı
```bash
sudo apt install ffmpeg
ffmpeg -version  # Kontrol
```

#### Tkinter hatası
```bash
sudo apt install python3-tk
```

#### Whisper model indirme hatası
```bash
# Manuel model indirme
python3 -c "import whisper; whisper.load_model('small')"
```

#### OpenCV hatası
```bash
pip install opencv-python-headless
```

#### Permission denied (install.sh)
```bash
chmod +x install.sh run.sh
```

---

## 🤝 Katkıda Bulunun

Katkılarınızı bekliyoruz! Detaylar için [CONTRIBUTING.md](CONTRIBUTING.md) dosyasına bakın.

```bash
# Fork ve clone
git clone https://github.com/YOUR_USERNAME/ffmpeg-youtube-shorts.git
cd ffmpeg-youtube-shorts

# Değişiklik yapın ve test edin
python3 main.py

# Pull request gönderin
```

---

## 📜 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## 👨‍💻 Geliştirici

**Ali Bedirhan**
- YouTube: [@ali_bedirhan](https://www.youtube.com/@ali_bedirhan)
- GitHub: [@alibedirhan](https://github.com/alibedirhan)

---

## 🙏 Teşekkürler

- [FFmpeg](https://ffmpeg.org/) - Video işleme
- [OpenAI Whisper](https://github.com/openai/whisper) - Ses tanıma
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern GUI
- [OpenCV](https://opencv.org/) - Görüntü işleme

---

<div align="center">

**⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!**

Made with ❤️ for Linux Content Creators

</div>
