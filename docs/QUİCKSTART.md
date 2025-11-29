# 🚀 Hızlı Başlangıç Rehberi

## 5 Dakikada Short Video Oluşturun!

### 1️⃣ Kurulum (Sadece İlk Kez)

```bash
# Projeyi indirin
git clone https://github.com/alibedirhan/linux-shorts-generator.git
cd linux-shorts-generator

# Otomatik kurulum
chmod +x install.sh
./install.sh
```

### 2️⃣ Başlatma

```bash
# Virtual environment'ı aktif edin
source venv/bin/activate

# Uygulamayı çalıştırın
python main.py
```

### 3️⃣ İlk Short'unuzu Oluşturun

1. **Video Seçin** 🎬
   - "Video Seç" butonuna tıklayın
   - Uzun videonuzu seçin (.mp4, .avi, .mkv, vb.)

2. **Zaman Belirleyin** ⏱️
   - Başlangıç: `00:02:30` (2 dakika 30 saniye)
   - Süre: `00:01:00` (1 dakika)

3. **Oluşturun** ✨
   - "Short Video Oluştur" butonuna basın
   - İşlem bitince `~/Videos/Shorts` klasöründe bulun!

### 4️⃣ Preset Kullanın (İsteğe Bağlı)

DPKG videonuz varsa:

1. Sağ panelden "DPKG Video Shorts" seçin
2. Listeden bir kesit seçin (örn: "APT vs DPKG Farkı")
3. "Kullan" butonuna tıklayın
4. Zaman değerleri otomatik dolar!

### 5️⃣ Ayarları Optimize Edin

**Hızlı İşlem İçin:**
- Kalite (CRF): 26
- FFmpeg Preset: fast

**Yüksek Kalite İçin:**
- Kalite (CRF): 20
- FFmpeg Preset: slow

---

## 💡 İpuçları

### Video Seçme
- En az 9:16 oran veya daha geniş videolar en iyi sonucu verir
- 1080p veya 4K videolar önerilir

### Zaman Formatı
- `HH:MM:SS` formatını kullanın
- Örnek: `00:05:30` = 5 dakika 30 saniye

### Shorts İçin İdeal Süre
- **15-60 saniye**: En viral aralık
- **60-90 saniye**: Bilgilendirici içerik
- **90+ saniye**: Detaylı anlatım

### Output Klasörü
- Tüm short'lar: `~/Videos/Shorts/`
- Dosya adı: `short_[video-adi]_[zaman].mp4`

---

## 🔧 Sorun Giderme

### "FFmpeg bulunamadı" Hatası
```bash
sudo apt update
sudo apt install ffmpeg
```

### "ModuleNotFoundError" Hatası
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### GUI Açılmıyor
```bash
# Gerekli paketleri kurun
sudo apt install python3-tk
```

---

## 📱 YouTube Shorts İçin Son Adımlar

1. Short'unuzu bulun: `~/Videos/Shorts/`
2. YouTube Studio'ya gidin
3. "Oluştur" → "Video yükle"
4. #Shorts hashtag'ini ekleyin
5. Başlık ve açıklama yazın
6. Yayınlayın! 🎉

---

## 📚 Daha Fazla Bilgi

- Detaylı kullanım: [README.md](../README.md)
- Preset oluşturma: [README.md#preset'ler](../README.md#-presetler)
- Sorunlar: [GitHub Issues](https://github.com/alibedirhan/linux-shorts-generator/issues)

---

**Başarılar! 🚀**
