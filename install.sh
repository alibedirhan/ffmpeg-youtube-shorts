#!/bin/bash
# LinuxShorts Pro v2.0 - Kurulum Scripti
# ======================================

echo "🎬 LinuxShorts Pro v2.0 Kurulum Başlıyor..."
echo "============================================"
echo ""

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Sistem paketlerini kontrol et
echo -e "${YELLOW}[1/4] Sistem paketleri kontrol ediliyor...${NC}"

# FFmpeg kontrolü
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}FFmpeg bulunamadı. Kuruluyor...${NC}"
    sudo apt update
    sudo apt install -y ffmpeg
else
    echo -e "${GREEN}✓ FFmpeg kurulu${NC}"
fi

# Python3 kontrolü
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3 bulunamadı. Kuruluyor...${NC}"
    sudo apt install -y python3 python3-pip python3-venv
else
    echo -e "${GREEN}✓ Python3 kurulu ($(python3 --version))${NC}"
fi

# Tkinter kontrolü
if ! python3 -c "import tkinter" &> /dev/null; then
    echo -e "${RED}Tkinter bulunamadı. Kuruluyor...${NC}"
    sudo apt install -y python3-tk
else
    echo -e "${GREEN}✓ Tkinter kurulu${NC}"
fi

# Font desteği
echo -e "${YELLOW}[2/4] Font desteği kontrol ediliyor...${NC}"
if [ ! -f "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" ]; then
    echo "DejaVu fontları kuruluyor..."
    sudo apt install -y fonts-dejavu-core
else
    echo -e "${GREEN}✓ DejaVu fontları kurulu${NC}"
fi

# Virtual environment oluştur
echo ""
echo -e "${YELLOW}[3/4] Python sanal ortamı oluşturuluyor...${NC}"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Sanal ortam oluşturuldu${NC}"
else
    echo -e "${GREEN}✓ Sanal ortam mevcut${NC}"
fi

# Sanal ortamı aktive et
source venv/bin/activate

# Pip güncelle
pip install --upgrade pip

# Python paketlerini kur
echo ""
echo -e "${YELLOW}[4/4] Python paketleri kuruluyor...${NC}"
echo "Bu işlem birkaç dakika sürebilir (Whisper modeli büyük)..."
echo ""

pip install -r requirements.txt

# Kurulum tamamlandı
echo ""
echo "============================================"
echo -e "${GREEN}✅ Kurulum Tamamlandı!${NC}"
echo "============================================"
echo ""
echo "Programı başlatmak için:"
echo ""
echo "  source venv/bin/activate"
echo "  python3 main.py"
echo ""
echo "veya kısaca:"
echo ""
echo "  ./run.sh"
echo ""
