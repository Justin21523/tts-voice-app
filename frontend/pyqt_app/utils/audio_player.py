# ============ frontend/pyqt_app/utils/audio_player.py ============
from PyQt6.QtCore import QObject, pyqtSignal, QUrl, QTimer
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
import os


class AudioPlayer(QObject):
    """Enhanced audio player with additional features"""

    position_changed = pyqtSignal(int)  # position in ms
    duration_changed = pyqtSignal(int)  # duration in ms
    state_changed = pyqtSignal(int)  # playback state
    volume_changed = pyqtSignal(float)  # volume (0.0 - 1.0)

    def __init__(self):
        super().__init__()
        self.media_player = None
        self.audio_output = None
        self.current_file = None
        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self._emit_position)

        self.setup_player()

    def setup_player(self):
        """Initialize the media player"""
        try:
            self.media_player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.media_player.setAudioOutput(self.audio_output)

            # Connect signals
            self.media_player.playbackStateChanged.connect(self._on_state_changed)
            self.media_player.durationChanged.connect(self.duration_changed.emit)
            self.audio_output.volumeChanged.connect(self.volume_changed.emit)

        except Exception as e:
            print(f"Failed to setup audio player: {e}")

    def load_file(self, file_path):
        """Load audio file for playback"""
        if not os.path.exists(file_path):
            return False

        try:
            url = QUrl.fromLocalFile(file_path)
            self.media_player.setSource(url)
            self.current_file = file_path
            return True
        except Exception as e:
            print(f"Failed to load audio file: {e}")
            return False

    def play(self):
        """Start playback"""
        if self.media_player and self.current_file:
            self.media_player.play()
            self.position_timer.start(100)  # Update every 100ms

    def pause(self):
        """Pause playback"""
        if self.media_player:
            self.media_player.pause()
            self.position_timer.stop()

    def stop(self):
        """Stop playback"""
        if self.media_player:
            self.media_player.stop()
            self.position_timer.stop()

    def set_position(self, position_ms):
        """Set playback position in milliseconds"""
        if self.media_player:
            self.media_player.setPosition(position_ms)

    def set_volume(self, volume):
        """Set volume (0.0 - 1.0)"""
        if self.audio_output:
            self.audio_output.setVolume(volume)

    def get_volume(self):
        """Get current volume"""
        if self.audio_output:
            return self.audio_output.volume()
        return 0.0

    def get_position(self):
        """Get current playback position in milliseconds"""
        if self.media_player:
            return self.media_player.position()
        return 0

    def get_duration(self):
        """Get total duration in milliseconds"""
        if self.media_player:
            return self.media_player.duration()
        return 0

    def is_playing(self):
        """Check if currently playing"""
        if self.media_player:
            return (
                self.media_player.playbackState()
                == QMediaPlayer.PlaybackState.PlayingState
            )
        return False

    def _on_state_changed(self, state):
        """Handle playback state changes"""
        self.state_changed.emit(state)

        if state != QMediaPlayer.PlaybackState.PlayingState:
            self.position_timer.stop()
        else:
            self.position_timer.start(100)

    def _emit_position(self):
        """Emit current position"""
        position = self.get_position()
        self.position_changed.emit(position)
