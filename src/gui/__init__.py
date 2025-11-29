"""LinuxShorts Pro - GUI modules"""

from .main_window import MainWindow, main

try:
    from .video_editor_tab import VideoEditorTab
except ImportError:
    pass
