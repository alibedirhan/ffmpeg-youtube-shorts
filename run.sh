#!/bin/bash
# LinuxShorts Pro v2.0 - Başlatma Scripti

# Script'in bulunduğu dizine git
cd "$(dirname "$0")"

# Sanal ortamı aktive et
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Programı başlat
python3 main.py
