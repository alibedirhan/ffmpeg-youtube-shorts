import sys
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGraphicsView, 
                             QGraphicsScene, QGraphicsTextItem, QVBoxLayout, 
                             QWidget, QPushButton, QSlider, QHBoxLayout, QLabel, QMessageBox)
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt6.QtCore import QUrl, Qt, QPointF, QSizeF, pyqtSignal

# Logger import (senin projenden)
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from logger import get_logger
logger = get_logger("LinuxShorts.Editor")

class DraggableSubtitle(QGraphicsTextItem):
    """Sürüklenebilir altyazı nesnesi"""
    position_changed = pyqtSignal(float, float)

    def __init__(self, text):
        super().__init__(text)
        self.setFlags(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable | 
                      QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable)
        
        # Görünüm Ayarları (Varsayılan)
        font = self.font()
        font.setPixelSize(40) # Önizleme için büyük font
        font.setBold(True)
        font.setFamily("Arial")
        self.setFont(font)
        self.setDefaultTextColor(Qt.GlobalColor.yellow)
        
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        # Yeni pozisyonu bildir
        self.position_changed.emit(self.pos().x(), self.pos().y())

class InteractiveEditor(QMainWindow):
    """Canva Benzeri Video Editörü"""
    
    def __init__(self, video_path: Path, srt_path: Path, on_save_callback=None):
        super().__init__()
        self.video_path = video_path
        self.srt_path = srt_path
        self.on_save_callback = on_save_callback
        self.subtitle_data = self._parse_srt(srt_path)
        
        self.setWindowTitle("LinuxShorts - İnteraktif Editör")
        self.resize(500, 900) # 9:16 formatına uygun pencere

        self.init_ui()
        self.load_video()

    def _parse_srt(self, srt_path):
        """SRT dosyasını basitçe parse eder"""
        segments = []
        try:
            with open(srt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            blocks = content.split('\n\n')
            for block in blocks:
                lines = block.split('\n')
                if len(lines) >= 3:
                    times = lines[1].split(' --> ')
                    start = self._time_to_ms(times[0])
                    end = self._time_to_ms(times[1])
                    text = "\n".join(lines[2:])
                    segments.append({'start': start, 'end': end, 'text': text})
        except Exception as e:
            logger.error(f"SRT Parse hatası: {e}")
        return segments

    def _time_to_ms(self, time_str):
        """00:00:00,000 -> milisaniye"""
        h, m, s_ms = time_str.replace(',', '.').split(':')
        s = float(s_ms)
        return int(h)*3600000 + int(m)*60000 + int(s*1000)

    def init_ui(self):
        # Sahne ve Görünüm
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setStyleSheet("background-color: #2c3e50;")
        
        # Video Katmanı
        self.player = QMediaPlayer()
        self.video_item = QGraphicsVideoItem()
        # Video boyutunu sabitleyelim (Preview için ölçekli)
        self.preview_width = 450
        self.preview_height = 800
        self.video_item.setSize(QSizeF(self.preview_width, self.preview_height))
        self.scene.addItem(self.video_item)
        self.player.setVideoOutput(self.video_item)
        
        # Altyazı Katmanı
        self.subtitle_item = DraggableSubtitle("Önizleme Metni")
        self.subtitle_item.setPos(50, 600) # Default konum
        self.scene.addItem(self.subtitle_item)
        
        # Layout
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)
        layout.addWidget(self.view)
        
        # Kontroller
        controls = QHBoxLayout()
        
        self.play_btn = QPushButton("▶ Oynat")
        self.play_btn.clicked.connect(self.toggle_play)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.sliderMoved.connect(self.set_position)
        
        self.save_btn = QPushButton("💾 KAYDET VE RENDER AL")
        self.save_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px;")
        self.save_btn.clicked.connect(self.save_and_close)

        controls.addWidget(self.play_btn)
        controls.addWidget(self.slider)
        
        layout.addLayout(controls)
        layout.addWidget(self.save_btn)

        # Sinyaller
        self.player.positionChanged.connect(self.on_position_changed)
        self.player.durationChanged.connect(self.on_duration_changed)

    def load_video(self):
        self.player.setSource(QUrl.fromLocalFile(str(self.video_path)))

    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.play_btn.setText("▶ Oynat")
        else:
            self.player.play()
            self.play_btn.setText("⏸ Duraklat")

    def on_position_changed(self, position):
        self.slider.setValue(position)
        # Altyazıyı senkronize et
        current_text = ""
        for seg in self.subtitle_data:
            if seg['start'] <= position <= seg['end']:
                current_text = seg['text']
                break
        
        # Metni güncelle ama pozisyonu koru
        self.subtitle_item.setPlainText(current_text)

    def on_duration_changed(self, duration):
        self.slider.setRange(0, duration)

    def set_position(self, position):
        self.player.setPosition(position)

    def save_and_close(self):
        """Koordinatları hesapla ve ana programa dön"""
        # Sahne üzerindeki Y pozisyonu
        y_pos = self.subtitle_item.pos().y()
        
        # FFmpeg için MarginV hesabı (Alttan uzaklık)
        # Preview yüksekliği 800px ise ve y_pos 600 ise, alttan 200px yukarıdadır.
        # Bunu gerçek video çözünürlüğüne (1920px) oranlamamız lazım.
        
        scale_factor = 1920 / self.preview_height
        margin_from_top = y_pos * scale_factor
        margin_v = 1920 - margin_from_top - 100 # 100px text yüksekliği tahmini
        
        if margin_v < 0: margin_v = 0
        
        settings = {
            'alignment': 2, # Bottom Center
            'margin_v': int(margin_v)
        }
        
        logger.info(f"Editörden dönen ayarlar: {settings}")
        
        if self.on_save_callback:
            self.on_save_callback(settings)
            
        self.close()

# Test için
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Dummy data ile test
    editor = InteractiveEditor(Path("test.mp4"), Path("test.srt"))
    editor.show()
    sys.exit(app.exec())
