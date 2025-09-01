# ============ frontend/pyqt_app/widgets/tts_widget.py ============
import time
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QComboBox,
    QSlider,
    QLabel,
    QProgressBar,
    QGroupBox,
    QSpinBox,
    QCheckBox,
    QMessageBox,
    QFileDialog,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent
import tempfile
import os
from pathlib import Path


class TTSThread(QThread):
    """Background thread for TTS processing"""

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, client, text, speaker_id, language, speed):
        super().__init__()
        self.client = client
        self.text = text
        self.speaker_id = speaker_id
        self.language = language
        self.speed = speed

    def run(self):
        try:
            result = self.client.text_to_speech(
                text=self.text,
                speaker_id=self.speaker_id,
                language=self.language,
                speed=self.speed,
            )

            if result.get("error"):
                self.error.emit(result["error"])
            else:
                self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))


class TTSWidget(QWidget):
    status_changed = pyqtSignal(str)

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.media_player = None
        self.audio_output = None
        self.current_audio_file = None
        self.tts_thread = None
        self.init_ui()
        self.load_profiles()

        # Setup media player
        self.setup_media_player()

    def init_ui(self):
        """Initialize TTS interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Text input group
        text_group = QGroupBox("Text Input")
        text_layout = QVBoxLayout(text_group)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Enter text to synthesize...")
        self.text_edit.setMaximumHeight(150)
        self.text_edit.setFont(QFont("Arial", 11))
        self.text_edit.textChanged.connect(self.update_char_count)
        text_layout.addWidget(self.text_edit)

        self.char_count_label = QLabel("0/1000 characters")
        self.char_count_label.setStyleSheet("color: gray;")
        text_layout.addWidget(self.char_count_label)

        layout.addWidget(text_group)

        # Settings group
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout(settings_group)

        # Speaker and language row
        row1 = QHBoxLayout()

        row1.addWidget(QLabel("Speaker:"))
        self.speaker_combo = QComboBox()
        self.speaker_combo.addItem("Default", "default")
        row1.addWidget(self.speaker_combo)

        row1.addWidget(QLabel("Language:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(
            [("Chinese", "zh"), ("English", "en"), ("Japanese", "ja")]
        )
        for i, (text, code) in enumerate(
            [("Chinese", "zh"), ("English", "en"), ("Japanese", "ja")]
        ):
            self.language_combo.setItemData(i, code)
        row1.addWidget(self.language_combo)

        settings_layout.addLayout(row1)

        # Speed control
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(5, 20)  # 0.5x to 2.0x
        self.speed_slider.setValue(10)  # 1.0x
        self.speed_slider.valueChanged.connect(self.update_speed_label)
        speed_layout.addWidget(self.speed_slider)

        self.speed_label = QLabel("1.0x")
        self.speed_label.setMinimumWidth(40)
        speed_layout.addWidget(self.speed_label)

        settings_layout.addLayout(speed_layout)
        layout.addWidget(settings_group)

        # Generate button
        self.generate_btn = QPushButton("🎤 Generate Speech")
        self.generate_btn.setMinimumHeight(40)
        self.generate_btn.setStyleSheet(
            """
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
            }
        """
        )
        self.generate_btn.clicked.connect(self.generate_speech)
        layout.addWidget(self.generate_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Results group
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout(results_group)

        self.result_label = QLabel("Click 'Generate Speech' to synthesize audio")
        self.result_label.setWordWrap(True)
        results_layout.addWidget(self.result_label)

        # Audio controls
        controls_layout = QHBoxLayout()

        self.play_btn = QPushButton("▶️ Play")
        self.play_btn.setEnabled(False)
        self.play_btn.clicked.connect(self.toggle_playback)
        controls_layout.addWidget(self.play_btn)

        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_playback)
        controls_layout.addWidget(self.stop_btn)

        self.save_btn = QPushButton("💾 Save")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_audio)
        controls_layout.addWidget(self.save_btn)

        results_layout.addLayout(controls_layout)
        layout.addWidget(results_group)

    def setup_media_player(self):
        """Setup Qt media player for audio playback"""
        try:
            self.media_player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.media_player.setAudioOutput(self.audio_output)

            # Connect media player signals
            self.media_player.playbackStateChanged.connect(
                self.on_playback_state_changed
            )
        except Exception as e:
            print(f"Failed to setup media player: {e}")

    def load_profiles(self):
        """Load speaker profiles from backend"""
        try:
            result = self.client.get_profiles()
            if result.get("profiles"):
                self.speaker_combo.clear()
                self.speaker_combo.addItem("Default", "default")
                for profile in result["profiles"]:
                    self.speaker_combo.addItem(profile["name"], profile["id"])
        except Exception as e:
            print(f"Failed to load profiles: {e}")

    def update_char_count(self):
        """Update character count display"""
        text = self.text_edit.toPlainText()
        count = len(text)
        self.char_count_label.setText(f"{count}/1000 characters")

        if count > 1000:
            self.char_count_label.setStyleSheet("color: red;")
        else:
            self.char_count_label.setStyleSheet("color: gray;")

    def update_speed_label(self):
        """Update speed display"""
        value = self.speed_slider.value()
        speed = value / 10.0
        self.speed_label.setText(f"{speed:.1f}x")

    def generate_speech(self):
        """Generate speech from text"""
        text = self.text_edit.toPlainText().strip()

        if not text:
            QMessageBox.warning(self, "Warning", "Please enter text to synthesize")
            return

        if len(text) > 1000:
            QMessageBox.warning(self, "Warning", "Text too long (max 1000 characters)")
            return

        # Get settings
        speaker_id = self.speaker_combo.currentData() or "default"
        language = self.language_combo.currentData() or "zh"
        speed = self.speed_slider.value() / 10.0

        # Disable UI and show progress
        self.set_ui_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.result_label.setText("🔄 Generating speech...")
        self.status_changed.emit("Generating speech...")

        # Start TTS thread
        self.tts_thread = TTSThread(self.client, text, speaker_id, language, speed)
        self.tts_thread.finished.connect(self.on_tts_finished)
        self.tts_thread.error.connect(self.on_tts_error)
        self.tts_thread.start()

    def on_tts_finished(self, result):
        """Handle TTS completion"""
        try:
            # Download audio file
            audio_url = result.get("audio_url")
            if not audio_url:
                self.on_tts_error("No audio URL in response")
                return

            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            temp_file.close()

            success = self.client.download_audio(audio_url, temp_file.name)
            if not success:
                self.on_tts_error("Failed to download audio")
                return

            self.current_audio_file = temp_file.name

            # Update UI
            duration = result.get("duration", 0)
            processing_time = result.get("processing_time", 0)

            self.result_label.setText(
                f"✅ Generation successful!\n"
                f"Duration: {duration:.1f}s | Processing: {processing_time:.1f}s"
            )

            # Enable audio controls
            self.play_btn.setEnabled(True)
            self.save_btn.setEnabled(True)

            # Setup media player with the audio file
            if self.media_player:
                self.media_player.setSource(QUrl.fromLocalFile(temp_file.name))

            self.status_changed.emit("Speech generated successfully")

        except Exception as e:
            self.on_tts_error(f"Error processing result: {str(e)}")
        finally:
            self.set_ui_enabled(True)
            self.progress_bar.setVisible(False)

    def on_tts_error(self, error_message):
        """Handle TTS error"""
        self.result_label.setText(f"❌ Error: {error_message}")
        self.status_changed.emit(f"TTS Error: {error_message}")
        self.set_ui_enabled(True)
        self.progress_bar.setVisible(False)

    def set_ui_enabled(self, enabled):
        """Enable/disable UI elements"""
        self.text_edit.setEnabled(enabled)
        self.speaker_combo.setEnabled(enabled)
        self.language_combo.setEnabled(enabled)
        self.speed_slider.setEnabled(enabled)
        self.generate_btn.setEnabled(enabled)

    def toggle_playback(self):
        """Toggle audio playback"""
        if not self.media_player or not self.current_audio_file:
            return

        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def stop_playback(self):
        """Stop audio playback"""
        if self.media_player:
            self.media_player.stop()

    def on_playback_state_changed(self, state):
        """Handle playback state changes"""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_btn.setText("⏸️ Pause")
            self.stop_btn.setEnabled(True)
        else:
            self.play_btn.setText("▶️ Play")
            self.stop_btn.setEnabled(False)

    def save_audio(self):
        """Save generated audio to file"""
        if not self.current_audio_file:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Audio",
            f"tts_output_{int(time.time())}.wav",
            "Audio Files (*.wav)",
        )

        if file_path:
            try:
                import shutil

                shutil.copy2(self.current_audio_file, file_path)
                QMessageBox.information(
                    self, "Success", f"Audio saved to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save audio:\n{str(e)}")
