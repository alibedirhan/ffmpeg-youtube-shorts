# 🤝 Katkıda Bulunma Rehberi

LinuxShorts Generator Pro'ya katkıda bulunmak istediğiniz için teşekkür ederiz! Bu rehber, projeye nasıl katkıda bulunabileceğinizi açıklar.

## 📋 İçindekiler

- [Davranış Kuralları](#davranış-kuralları)
- [Nasıl Katkıda Bulunabilirim?](#nasıl-katkıda-bulunabilirim)
- [Geliştirme Ortamı Kurulumu](#geliştirme-ortamı-kurulumu)
- [Kod Standartları](#kod-standartları)
- [Pull Request Süreci](#pull-request-süreci)
- [Hata Bildirimi](#hata-bildirimi)
- [Özellik Önerisi](#özellik-önerisi)

---

## 📜 Davranış Kuralları

Bu proje, açık ve kapsayıcı bir topluluk oluşturmayı hedefler. Lütfen:

- ✅ Saygılı ve yapıcı olun
- ✅ Farklı bakış açılarına açık olun
- ✅ Eleştirileri nazikçe kabul edin
- ❌ Hakaret, taciz veya aşağılayıcı davranışlardan kaçının
- ❌ Kişisel saldırılardan kaçının

---

## 🛠️ Nasıl Katkıda Bulunabilirim?

### 1. Hata Düzeltmeleri
- Mevcut hataları düzeltin
- Testler ekleyin
- Performans iyileştirmeleri yapın

### 2. Yeni Özellikler
- Roadmap'teki özellikleri geliştirin
- Yeni modüller ekleyin
- UI/UX iyileştirmeleri yapın

### 3. Dökümantasyon
- README'yi güncelleyin
- Kod yorumları ekleyin
- Kullanım örnekleri yazın

### 4. Çeviri
- Türkçe dışındaki dillere çeviri yapın
- Mevcut çevirileri iyileştirin

### 5. Test
- Uygulamayı test edin
- Hata bildirin
- Edge case'leri belirleyin

---

## 💻 Geliştirme Ortamı Kurulumu

### Ön Gereksinimler

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y git python3 python3-pip python3-venv python3-tk ffmpeg
```

### Fork ve Clone

```bash
# 1. GitHub'da projeyi fork edin

# 2. Fork'unuzu klonlayın
git clone https://github.com/YOUR_USERNAME/ffmpeg-youtube-shorts.git
cd ffmpeg-youtube-shorts

# 3. Upstream remote ekleyin
git remote add upstream https://github.com/alibedirhan/ffmpeg-youtube-shorts.git
```

### Sanal Ortam

```bash
# Sanal ortam oluşturun
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları kurun
pip install --upgrade pip
pip install -r requirements.txt

# Geliştirme bağımlılıkları (opsiyonel)
pip install pylint black isort
```

### Test Etme

```bash
# Uygulamayı çalıştırın
python3 main.py

# Syntax kontrolü
python3 -m py_compile src/gui/main_window.py
```

---

## 📏 Kod Standartları

### Python Stili

- **PEP 8** standartlarına uyun
- **4 boşluk** indentasyon kullanın
- Satır uzunluğu maksimum **100 karakter**
- Fonksiyon ve sınıf isimleri **snake_case** / **PascalCase**

### Örnek

```python
class MyClass:
    """Sınıf açıklaması."""
    
    def __init__(self, param: str):
        """
        Yapıcı metod.
        
        Args:
            param: Parametre açıklaması
        """
        self.param = param
    
    def my_method(self) -> bool:
        """Metod açıklaması."""
        return True
```

### Commit Mesajları

Türkçe veya İngilizce commit mesajları kullanabilirsiniz:

```
feat: Yeni özellik ekle
fix: Hata düzelt
docs: Dökümantasyon güncelle
style: Kod formatı düzenle
refactor: Kod yapısını iyileştir
test: Test ekle
chore: Bakım işleri
```

**Örnekler:**
```
feat: Altyazı renk seçici eklendi
fix: Export sırasında crash düzeltildi
docs: README kurulum bölümü güncellendi
```

---

## 🔄 Pull Request Süreci

### 1. Branch Oluşturun

```bash
# Main'i güncelleyin
git checkout main
git pull upstream main

# Yeni branch oluşturun
git checkout -b feature/yeni-ozellik
# veya
git checkout -b fix/hata-duzeltme
```

### 2. Değişiklik Yapın

```bash
# Değişikliklerinizi yapın
# Test edin
python3 main.py

# Commit edin
git add .
git commit -m "feat: Yeni özellik eklendi"
```

### 3. Push Edin

```bash
git push origin feature/yeni-ozellik
```

### 4. Pull Request Açın

1. GitHub'da fork'unuza gidin
2. "Compare & pull request" butonuna tıklayın
3. Değişikliklerinizi açıklayın
4. PR'ı gönderin

### PR Kontrol Listesi

- [ ] Kod çalışıyor ve test edildi
- [ ] Syntax hataları yok
- [ ] Commit mesajları açıklayıcı
- [ ] Gerekirse dökümantasyon güncellendi
- [ ] Mevcut testler geçiyor

---

## 🐛 Hata Bildirimi

### Issue Açmadan Önce

1. Mevcut issue'ları kontrol edin
2. Son sürümü kullandığınızdan emin olun
3. Hatayı tekrarlayabildiğinizi doğrulayın

### Issue Şablonu

```markdown
## Hata Açıklaması
[Hatayı kısaca açıklayın]

## Tekrarlama Adımları
1. '...' butonuna tıklayın
2. '...' sayfasına gidin
3. Hatayı görün

## Beklenen Davranış
[Ne olması gerektiğini açıklayın]

## Gerçekleşen Davranış
[Ne olduğunu açıklayın]

## Ekran Görüntüsü
[Varsa ekleyin]

## Ortam
- OS: Ubuntu 22.04
- Python: 3.11
- LinuxShorts: v2.0
```

---

## 💡 Özellik Önerisi

### Issue Şablonu

```markdown
## Özellik Açıklaması
[Özelliği kısaca açıklayın]

## Neden Gerekli?
[Bu özelliğin neden faydalı olacağını açıklayın]

## Olası Çözüm
[Nasıl implement edilebileceğini açıklayın]

## Alternatifler
[Düşündüğünüz alternatifleri listeleyin]
```

---

## 🗺️ Roadmap

### Planlanan Özellikler

- [ ] Video oynatma (play/pause)
- [ ] Çoklu segment desteği
- [ ] Batch processing
- [ ] Watermark ekleme
- [ ] Aspect ratio seçenekleri (1:1, 4:5)
- [ ] Müzik ekleme
- [ ] Preset kaydetme

### Katkı Fırsatları

Bu özelliklerden birini geliştirmek isterseniz, önce issue açın ve planınızı paylaşın.

---

## 📞 İletişim

- **GitHub Issues**: Hata ve öneriler için
- **Pull Requests**: Kod katkıları için

---

## 🙏 Teşekkürler

Tüm katkıda bulunanlara teşekkür ederiz! Her türlü katkı değerlidir:

- Kod yazanlar
- Hata bildirenler
- Dökümantasyon yazanlar
- Test edenler
- Fikir verenler

**Katkılarınız için teşekkürler! 🎉**
