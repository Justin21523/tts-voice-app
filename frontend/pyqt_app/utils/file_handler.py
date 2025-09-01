# ============ frontend/pyqt_app/utils/file_handler.py ============
import os
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal


class FileHandler(QObject):
    """Utility class for file operations"""

    file_processed = pyqtSignal(str, dict)  # file_path, metadata

    def __init__(self):
        super().__init__()
        self.supported_audio_formats = [".wav", ".mp3", ".ogg", ".m4a", ".flac"]
        self.max_file_size_mb = 50

    def is_valid_audio_file(self, file_path):
        """Check if file is a valid audio file"""
        if not os.path.exists(file_path):
            return False, "File does not exist"

        # Check extension
        ext = Path(file_path).suffix.lower()
        if ext not in self.supported_audio_formats:
            return (
                False,
                f"Unsupported format. Supported: {', '.join(self.supported_audio_formats)}",
            )

        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            return (
                False,
                f"File too large ({file_size_mb:.1f}MB). Max size: {self.max_file_size_mb}MB",
            )

        return True, "Valid audio file"

    def get_file_metadata(self, file_path):
        """Get basic file metadata"""
        try:
            stat = os.stat(file_path)
            return {
                "filename": os.path.basename(file_path),
                "size_bytes": stat.st_size,
                "size_mb": stat.st_size / (1024 * 1024),
                "modified": stat.st_mtime,
                "extension": Path(file_path).suffix.lower(),
            }
        except Exception as e:
            return {"error": str(e)}

    def process_dropped_files(self, file_paths):
        """Process list of dropped files"""
        audio_files = []

        for file_path in file_paths:
            valid, message = self.is_valid_audio_file(file_path)

            if valid:
                metadata = self.get_file_metadata(file_path)
                audio_files.append((file_path, metadata))
                self.file_processed.emit(file_path, metadata)

        return audio_files
