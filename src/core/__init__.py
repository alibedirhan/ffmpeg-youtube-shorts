"""LinuxShorts Pro - Core modules"""

from .ffmpeg_wrapper import FFmpegWrapper, VideoInfo
from .subtitle_generator import SubtitleGenerator, SubtitleSegment
from .video_analyzer import VideoAnalyzer, VideoSegment
from .hashtag_generator import HashtagGenerator

# Video Editor
try:
    from .video_editor import ProVideoEditor, VideoTransform
except ImportError:
    pass

# Preset Manager
try:
    from .preset_manager import PresetManager, VideoPreset
except ImportError:
    pass

# Smart Analyzer (Akıllı Kesit, Hook Detector, Sahne Algılama)
try:
    from .smart_analyzer import SmartVideoAnalyzer, Segment, AnalysisResult
except ImportError:
    pass

# SEO Generator
try:
    from .seo_generator import SEOGenerator, SEOSuggestion, VideoMetadata
except ImportError:
    pass

# Thumbnail Generator
try:
    from .thumbnail_generator import ThumbnailGenerator, ThumbnailStyle, FrameCandidate
except ImportError:
    pass
