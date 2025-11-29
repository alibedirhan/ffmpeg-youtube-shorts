# 📖 LinuxShorts Generator Pro - Detaylı Kullanım Kılavuzu

Bu kılavuz, LinuxShorts Generator Pro'nun tüm özelliklerini detaylı olarak açıklar.

---

## 📑 İçindekiler

1. [Başlarken](#1-başlarken)
2. [Ana Sayfa](#2-ana-sayfa)
3. [Video Düzenleme](#3-video-düzenleme)
4. [Akıllı Analiz](#4-akıllı-analiz)
5. [Altyazı Oluşturma](#5-altyazı-oluşturma)
6. [Thumbnail](#6-thumbnail)
7. [SEO & Hashtag](#7-seo--hashtag)
8. [Export](#8-export)
9. [İpuçları ve Püf Noktaları](#9-ipuçları-ve-püf-noktaları)
10. [Sık Sorulan Sorular](#10-sık-sorulan-sorular)

---

## 1. Başlarken

### Program Arayüzü

```
┌─────────────────────────────────────────────────────────────┐
│                    LinuxShorts Pro v2.0                     │
├────────────┬────────────────────────────────────────────────┤
│            │                                                │
│  SIDEBAR   │              ANA İÇERİK ALANI                  │
│            │                                                │
│ 🏠 Ana     │   Seçilen sayfanın içeriği burada görünür     │
│ 🎬 Video   │                                                │
│ 🧠 Analiz  │                                                │
│ 📝 Altyazı │                                                │
│ 🖼️ Thumb   │                                                │
│ 📊 SEO     │                                                │
│ 🚀 Export  │                                                │
│            │                                                │
├────────────┴────────────────────────────────────────────────┤
│  📹 video.mp4  │  📐 1920x1080  │  ⏱️ 300.5s               │
└─────────────────────────────────────────────────────────────┘
```

### Tipik İş Akışı

```
1. Ana Sayfa → Video Seç
       ↓
2. Video Düzenle → Zoom, Pozisyon, Zaman Aralığı
       ↓
3. Altyazı (opsiyonel) → Whisper ile oluştur
       ↓
4. SEO (opsiyonel) → Başlık ve hashtag al
       ↓
5. Export → SHORT OLUŞTUR
       ↓
6. YouTube'a Yükle!
```

---

## 2. Ana Sayfa

### Video Seçme

1. `📁 Video Seç` butonuna tıklayın
2. Dosya seçici açılır
3. Video dosyanızı seçin

### Desteklenen Formatlar

| Format | Uzantı | Notlar |
|--------|--------|--------|
| MPEG-4 | .mp4 | En yaygın, önerilen |
| AVI | .avi | Eski format |
| Matroska | .mkv | Çoklu ses/altyazı |
| QuickTime | .mov | Apple formatı |
| WebM | .webm | Web optimize |

### Video Bilgisi

Video seçildikten sonra alt kısımda bilgiler görünür:

```
📹 video.mp4
📐 1920x1080
⏱️ 300.5s
```

---

## 3. Video Düzenleme

En önemli sayfa! Burada videonuzu YouTube Shorts formatına dönüştürürsünüz.

### 3.1 Önizleme Alanı

```
┌─────────────────────────────────────┐
│                                     │
│         [Video Preview]             │
│                                     │
│     Fare ile sürükle → Pozisyon     │
│     Scroll → Zoom in/out            │
│                                     │
└─────────────────────────────────────┘
         ──────●──────────────────
         00:15 / 05:30
```

### 3.2 Fare Kontrolleri

| Eylem | Sonuç |
|-------|-------|
| **Sol tık + sürükle** | Video pozisyonunu değiştir |
| **Scroll yukarı** | Zoom in (%1) |
| **Scroll aşağı** | Zoom out (%1) |

### 3.3 Transform Kontrolleri

#### Ölçek (Zoom)

```
Ölçek: ──────────●────────── 100%
       30%                   300%
```

- **%100**: Video tam olarak canvas'a sığar (fit)
- **<%100**: Video daha küçük, daha fazla arka plan
- **>%100**: Video daha büyük, kenarlar kırpılır

#### Pozisyon

```
X Pozisyon: ──────●────── 0
            -200        200

Y Pozisyon: ──────●────── 0
            -200        200
```

#### Hızlı Butonlar

| Buton | İşlev |
|-------|-------|
| **Ortala** | Pozisyonu (0, 0) yapar |
| **Sığdır** | Zoom'u %100 yapar (fit) |
| **Doldur** | Zoom'u ekranı dolduracak şekilde ayarlar |
| **Sıfırla** | Her şeyi varsayılana döndürür |

### 3.4 Zaman Aralığı

```
Başlangıç: [00:01:30]    Süre: [60]
```

#### Başlangıç Zamanı

- Format: `HH:MM:SS` veya `MM:SS` veya sadece saniye
- Örnekler: `00:01:30`, `01:30`, `90`
- Slider ile senkronize çalışır

#### Süre

- Saniye cinsinden
- YouTube Shorts için maksimum **60 saniye**

### 3.5 Arka Plan Modları

```
⬛ Siyah    🌫️ Blur    🎨 Renk
```

#### Siyah
- Klasik siyah kenarlar
- En basit seçenek

#### Blur (Önerilen)
- Video'nun bulanıklaştırılmış hali arka plan olur
- Profesyonel görünüm
- **Blur Gücü**: 5-51 arası ayarlanabilir

#### Renk
- Özel renk seçebilirsiniz
- Renk seçici açılır

### 3.6 Kalite Ayarları

#### CRF (Constant Rate Factor)

```
CRF: ──────●────── 23
     15           35
```

| Değer | Kalite | Dosya Boyutu |
|-------|--------|--------------|
| 15-18 | Çok yüksek | Büyük |
| 19-23 | Yüksek (önerilen) | Orta |
| 24-28 | Orta | Küçük |
| 29-35 | Düşük | Çok küçük |

#### Preset (Hız)

| Preset | Hız | Kalite |
|--------|-----|--------|
| ultrafast | ⚡⚡⚡⚡⚡ | ⭐ |
| fast | ⚡⚡⚡⚡ | ⭐⭐ |
| medium | ⚡⚡⚡ | ⭐⭐⭐ |
| slow | ⚡⚡ | ⭐⭐⭐⭐ |
| veryslow | ⚡ | ⭐⭐⭐⭐⭐ |

---

## 4. Akıllı Analiz

Video'nuzu otomatik olarak analiz eder ve en iyi kesitleri önerir.

### 4.1 Analiz Başlatma

1. `🔍 Analizi Başlat` butonuna tıklayın
2. Progress bar'ı izleyin
3. Sonuçları görün

### 4.2 Analiz Edilen Özellikler

| Özellik | Açıklama |
|---------|----------|
| **Sessizlik Bölümleri** | Sessiz anlar tespit edilir |
| **Konuşma Bölümleri** | Aktif konuşma bölümleri |
| **Sahne Değişiklikleri** | Görsel geçişler |
| **Hook Adayları** | İzleyiciyi yakalayacak anlar |
| **En İyi Kesitler** | Skor bazlı öneriler |

### 4.3 Sonuçları Kullanma

```
⭐ En İyi Kesiti Kullan
```

Bu butona tıkladığınızda:
- Başlangıç zamanı otomatik ayarlanır
- Süre otomatik ayarlanır
- Video Düzenleme sayfasına yönlendirilirsiniz

---

## 5. Altyazı Oluşturma

OpenAI Whisper ile otomatik Türkçe altyazı oluşturun.

### 5.1 Sol Panel - Oluşturma

#### Model Seçimi

```
Model: [small ▼]
```

| Model | Hız | Doğruluk | İndirme |
|-------|-----|----------|---------|
| tiny | 10x | 60% | 75 MB |
| base | 5x | 70% | 150 MB |
| **small** | 2x | 85% | 500 MB |
| medium | 1x | 92% | 1.5 GB |
| large | 0.5x | 97% | 3 GB |

> **Öneri**: `small` model hız/doğruluk dengesi için idealdir.

#### Zaman Aralığı Seçeneği

```
☑ Sadece seçilen zaman aralığı için oluştur
```

- ✅ İşaretli: Video Düzenleme'deki zaman aralığı kullanılır
- ❌ İşaretsiz: Tüm video için altyazı oluşturulur

### 5.2 Sağ Panel - Düzenleme

Oluşturulan altyazı SRT formatında görünür:

```
1
00:00:00,000 --> 00:00:03,500
Merhaba arkadaşlar

2
00:00:03,500 --> 00:00:07,200
Bugün DPKG paket yöneticisini öğreneceğiz
```

#### Düzenleme Butonları

| Buton | İşlev |
|-------|-------|
| **💾 SRT Kaydet** | Dosyaya kaydet |
| **📋 Kopyala** | Panoya kopyala |

### 5.3 Altyazı Stili

```
Pozisyon: ⚫Üst  ⚫Orta  ●Alt
Font: ────────●────── 16px (8-48)
Renk: [████]
☑ Yarı saydam arka plan
```

---

## 6. Thumbnail

YouTube için göz alıcı küçük resimler oluşturun.

### 6.1 Frame Seçimi

```
Zaman: ────●────────── 15s
```

Slider'ı sürükleyerek istediğiniz kareyi seçin.

### 6.2 En İyi Frame Bulma

```
🔍 En İyi Frame'leri Bul
```

Otomatik olarak:
- Yüksek kontrast
- İyi parlaklık
- Keskinlik
- Yüz algılama (varsa)

### 6.3 Efektler

| Efekt | Aralık | Varsayılan |
|-------|--------|------------|
| **Parlaklık** | 50-150% | 110% |
| **Kontrast** | 50-150% | 120% |
| **Doygunluk** | 50-150% | 100% |
| **Vignette** | Açık/Kapalı | Açık |

### 6.4 Başlık Ekleme

```
Başlık Metni: [DPKG Nedir?]
```

Thumbnail'e büyük, gölgeli metin ekler.

### 6.5 Kaydetme

```
💾 Thumbnail Kaydet
```

- PNG veya JPG formatı
- 1280x720 çözünürlük (YouTube standart)

---

## 7. SEO & Hashtag

YouTube için optimize edilmiş başlık, açıklama ve hashtag önerileri.

### 7.1 Konu Girişi

```
Konu: [dpkg paket yönetimi]
```

### 7.2 Öneriler Al

```
✨ Öneriler Al
```

### 7.3 Sonuçlar

```
Başlık: DPKG Nedir? Linux Paket Yönetimi 🐧

Hashtags:
#linux #dpkg #ubuntu #türkçe #shorts #tutorial

Açıklama:
🎯 DPKG paket yönetimi hakkında bilmeniz gereken her şey!
👍 Beğenmeyi ve abone olmayı unutma!
```

### 7.4 Kopyalama

```
📋 Tümünü Kopyala
```

Tek tıkla başlık + açıklama + hashtag'leri kopyalar.

---

## 8. Export

Tüm ayarları uygulayıp final videoyu oluşturun.

### 8.1 Video Özeti

```
📹 1.mp4
📐 1920x1080
⏱️ 881.1 saniye
🎞️ 30.0 FPS
```

### 8.2 Seçenekler

#### Altyazı Gömme

```
☑ Altyazıyı videoya göm (burn-in)
```

- ✅ İşaretli: Altyazı video'nun içine yazılır
- ❌ İşaretsiz: Sadece video export edilir

#### Çıktı Dizini

```
Çıktı Dizini: [~/linuxshorts_output] [📁]
```

### 8.3 Export Başlatma

```
🚀 SHORT OLUŞTUR
```

### 8.4 Tamamlanma

```
✅ Tamamlandı: video_short.mp4
[Dosya konumunu aç?]
```

---

## 9. İpuçları ve Püf Noktaları

### YouTube Shorts İçin

1. **Süre**: Maksimum 60 saniye
2. **İlk 3 saniye**: HOOK! İzleyiciyi yakala
3. **Altyazı**: Sessiz izleyenler için şart
4. **Dikey Format**: 9:16 (1080x1920)
5. **#shorts**: Hashtag'i mutlaka ekle

### Yatay → Dikey Dönüşüm

```
Yatay Video (16:9)     Dikey Video (9:16)
┌────────────────┐     ┌──────────┐
│                │     │ ░░░░░░░░ │ ← Blur arka plan
│    İçerik      │ →   │ ┌──────┐ │
│                │     │ │İçerik│ │
└────────────────┘     │ └──────┘ │
                       │ ░░░░░░░░ │
                       └──────────┘
```

**Öneri**: "Doldur" butonunu kullanın, sonra içeriği fare ile konumlandırın.

### Performans

- **Küçük video**: `tiny` veya `base` model
- **Uzun video**: `small` model
- **Kaliteli sonuç**: `medium` model
- **SSD**: Daha hızlı işleme

### Kalite vs Boyut

| Senaryo | CRF | Preset |
|---------|-----|--------|
| Hızlı test | 28 | fast |
| Normal kullanım | 23 | medium |
| Yüksek kalite | 18 | slow |

---

## 10. Sık Sorulan Sorular

### Video çok küçük görünüyor?

**Çözüm**: "Doldur" butonuna tıklayın veya zoom'u artırın.

### Altyazı oluşturma çok yavaş?

**Çözüm**: Daha küçük model seçin (tiny, base).

### Export başarısız oluyor?

**Kontrol edin**:
1. FFmpeg kurulu mu?
2. Disk alanı yeterli mi?
3. Video dosyası bozuk mu?

### Whisper model inmiyor?

```bash
# Manuel indirme
python3 -c "import whisper; whisper.load_model('small')"
```

### Türkçe karakterler bozuk?

**Çözüm**: Font ayarlarını kontrol edin, DejaVu fontları kurun:
```bash
sudo apt install fonts-dejavu-core
```

---

## 📞 Destek

- **GitHub Issues**: [github.com/alibedirhan/ffmpeg-youtube-shorts/issues](https://github.com/alibedirhan/ffmpeg-youtube-shorts/issues)
- **YouTube**: [@alibedirhan](https://youtube.com/@alibedirhan)

---

**İyi içerikler! 🎬**
