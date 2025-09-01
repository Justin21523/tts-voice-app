# ============ frontend/pyqt_app/widgets/vc_widget.py ============
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QLabel,
    QProgressBar,
    QGroupBox,
    QCheckBox,
    QMessageBox,
    QFileDialog,
    QFrame,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QMimeData
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QFont
import tempfile
import os
import time
from pathlib import Path


class VCThread(QThread):
    """Background thread for VC processing"""

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, client, audio_file, target_speaker, preserve_pitch):
        super().__init__()
        self.client = client
        self.audio_file = audio_file
        self.target_speaker = target_speaker
        self.preserve_pitch = preserve_pitch

    def run(self):
        try:
            result = self.client.voice_conversion(
                audio_file=self.audio_file,
                target_speaker=self.target_speaker,
                preserve_pitch=self.preserve_pitch,
            )

            if result.get("error"):
                self.error.emit(result["error"])
            else:
                self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))


class DropArea(QFrame):
    """Drag and drop area for audio files"""

    file_dropped = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumHeight(120)
        self.setStyleSheet(
            """
            QFrame {
                border: 2px dashed #9ca3af;
                border-radius: 8px;
                background-color: #f9fafb;
                color: #6b7280;
            }
            QFrame:hover {
                border-color: #2563eb;
                background-color: #eff6ff;
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icon and text
        icon_label = QLabel("📁")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFont(QFont("Arial", 24))
        layout.addWidget(icon_label)

        text_label = QLabel("Drop audio file here\nor click to browse")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setWordWrap(True)
        layout.addWidget(text_label)

        hint_label = QLabel("Supports WAV, MP3, OGG, M4A, FLAC")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_label.setStyleSheet("color: #9ca3af; font-size: 12px;")
        layout.addWidget(hint_label)

    def mousePressEvent(self, event):
        """Handle click to browse files"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.browse_file()

    def browse_file(self):
        """Open file browser"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            "Audio Files (*.wav *.mp3 *.ogg *.m4a *.flac);;All Files (*)",
        )

        if file_path:
            self.file_dropped.emit(file_path)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Handle file drop"""
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            # Validate file type
            file_path = files[0]
            valid_exts = [".wav", ".mp3", ".ogg", ".m4a", ".flac"]
            if any(file_path.lower().endswith(ext) for ext in valid_exts):
                self.file_dropped.emit(file_path)
            else:
                QMessageBox.warning(
                    self,
                    "Invalid File",
                    "Please select a valid audio file (WAV, MP3, OGG, M4A, FLAC)",
                )


class VCWidget(QWidget):
    status_changed = pyqtSignal(str)

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.media_player = None
        self.audio_output = None
        self.source_file = None
        self.converted_file = None
        self.vc_thread = None
        self.init_ui()
        self.load_profiles()
        self.setup_media_player()

    def init_ui(self):
        """Initialize VC interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # File upload group
        upload_group = QGroupBox("Source Audio")
        upload_layout = QVBoxLayout(upload_group)

        self.drop_area = DropArea()
        self.drop_area.file_dropped.connect(self.load_source_file)
        upload_layout.addWidget(self.drop_area)

        self.source_info = QLabel("No file selected")
        self.source_info.setStyleSheet("color: gray; font-size: 12px;")
        upload_layout.addWidget(self.source_info)

        layout.addWidget(upload_group)

        # Settings group
        settings_group = QGroupBox("Conversion Settings")
        settings_layout = QVBoxLayout(settings_group)

        # Target speaker
        speaker_layout = QHBoxLayout()
        speaker_layout.addWidget(QLabel("Target Speaker:"))

        self.target_speaker_combo = QComboBox()
        self.target_speaker_combo.setMinimumWidth(200)
        speaker_layout.addWidget(self.target_speaker_combo)

        speaker_layout.addStretch()
        settings_layout.addLayout(speaker_layout)

        # Options
        self.preserve_pitch_cb = QCheckBox("Preserve Pitch")
        self.preserve_pitch_cb.setChecked(True)
        self.preserve_pitch_cb.setToolTip("Maintain original pitch characteristics")
        settings_layout.addWidget(self.preserve_pitch_cb)

        layout.addWidget(settings_group)

        # Convert button
        self.convert_btn = QPushButton("🎭 Convert Voice")
        self.convert_btn.setMinimumHeight(40)
        self.convert_btn.setEnabled(False)
        self.convert_btn.setStyleSheet(
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
            QPushButton:hover:enabled {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
            }
        """
        )
        self.convert_btn.clicked.connect(self.convert_voice)
        layout.addWidget(self.convert_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Results group
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout(results_group)

        self.result_label = QLabel("Upload audio and select target speaker to convert")
        self.result_label.setWordWrap(True)
        results_layout.addWidget(self.result_label)

        # Audio controls
        controls_layout = QHBoxLayout()

        self.play_original_btn = QPushButton("▶️ Play Original")
        self.play_original_btn.setEnabled(False)
        self.play_original_btn.clicked.connect(self.play_original)
        controls_layout.addWidget(self.play_original_btn)

        self.play_converted_btn = QPushButton("▶️ Play Converted")
        self.play_converted_btn.setEnabled(False)
        self.play_converted_btn.clicked.connect(self.play_converted)
        controls_layout.addWidget(self.play_converted_btn)

        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_playback)
        controls_layout.addWidget(self.stop_btn)

        self.save_btn = QPushButton("💾 Save")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_converted_audio)
        controls_layout.addWidget(self.save_btn)

        results_layout.addLayout(controls_layout)
        layout.addWidget(results_group)

    def setup_media_player(self):
        """Setup Qt media player"""
        try:
            self.media_player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.media_player.setAudioOutput(self.audio_output)
            self.media_player.playbackStateChanged.connect(
                self.on_playback_state_changed
            )
        except Exception as e:
            print(f"Failed to setup media player: {e}")

    def load_profiles(self):
        """Load target speaker profiles"""
        try:
            result = self.client.get_profiles()
            if result.get("profiles"):
                self.target_speaker_combo.clear()
                for profile in result["profiles"]:
                    self.target_speaker_combo.addItem(profile["name"], profile["id"])
                self.update_convert_button_state()
        except Exception as e:
            print(f"Failed to load profiles: {e}")

    def load_source_file(self, file_path):
        """Load source audio file"""
        try:
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)

            if file_size_mb > 50:
                QMessageBox.warning(
                    self,
                    "File Too Large",
                    f"File size ({file_size_mb:.1f}MB) exceeds 50MB limit",
                )
                return

            self.source_file = file_path
            filename = os.path.basename(file_path)
            self.source_info.setText(f"📎 {filename} ({file_size_mb:.1f}MB)")
            self.source_info.setStyleSheet("color: green; font-size: 12px;")

            self.play_original_btn.setEnabled(True)
            self.update_convert_button_state()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")

    def update_convert_button_state(self):
        """Update convert button enabled state"""
        has_source = self.source_file is not None
        has_target = self.target_speaker_combo.count() > 0
        self.convert_btn.setEnabled(has_source and has_target)

    def convert_voice(self):
        """Start voice conversion"""
        if not self.source_file:
            QMessageBox.warning(self, "Warning", "Please select source audio file")
            return

        target_speaker = self.target_speaker_combo.currentData()
        if not target_speaker:
            QMessageBox.warning(self, "Warning", "Please select target speaker")
            return

        # Disable UI and show progress
        self.set_ui_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.result_label.setText("🔄 Converting voice...")
        self.status_changed.emit("Converting voice...")

        # Start VC thread
        preserve_pitch = self.preserve_pitch_cb.isChecked()
        self.vc_thread = VCThread(
            self.client, self.source_file, target_speaker, preserve_pitch
        )
        self.vc_thread.finished.connect(self.on_vc_finished)
        self.vc_thread.error.connect(self.on_vc_error)
        self.vc_thread.start()

    def on_vc_finished(self, result):
        """Handle VC completion"""
        try:
            # Download converted audio
            audio_url = result.get("audio_url")
            if not audio_url:
                self.on_vc_error("No audio URL in response")
                return

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            temp_file.close()

            success = self.client.download_audio(audio_url, temp_file.name)
            if not success:
                self.on_vc_error("Failed to download converted audio")
                return

            self.converted_file = temp_file.name

            # Update UI
            processing_time = result.get("processing_time", 0)
            self.result_label.setText(
                f"✅ Conversion successful!\n"
                f"Processing time: {processing_time:.1f}s"
            )

            # Enable controls
            self.play_converted_btn.setEnabled(True)
            self.save_btn.setEnabled(True)

            self.status_changed.emit("Voice conversion completed")

        except Exception as e:
            self.on_vc_error(f"Error processing result: {str(e)}")
        finally:
            self.set_ui_enabled(True)
            self.progress_bar.setVisible(False)

    def on_vc_error(self, error_message):
        """Handle VC error"""
        self.result_label.setText(f"❌ Error: {error_message}")
        self.status_changed.emit(f"VC Error: {error_message}")
        self.set_ui_enabled(True)
        self.progress_bar.setVisible(False)

    def set_ui_enabled(self, enabled):
        """Enable/disable UI elements"""
        self.drop_area.setEnabled(enabled)
        self.target_speaker_combo.setEnabled(enabled)
        self.preserve_pitch_cb.setEnabled(enabled)
        self.convert_btn.setEnabled(
            enabled and self.source_file and self.target_speaker_combo.count() > 0
        )

    def play_original(self):
        """Play original audio"""
        if self.source_file and self.media_player:
            self.media_player.setSource(QUrl.fromLocalFile(self.source_file))
            self.media_player.play()

    def play_converted(self):
        """Play converted audio"""
        if self.converted_file and self.media_player:
            self.media_player.setSource(QUrl.fromLocalFile(self.converted_file))
            self.media_player.play()

    def stop_playback(self):
        """Stop audio playback"""
        if self.media_player:
            self.media_player.stop()

    def on_playback_state_changed(self, state):
        """Handle playback state changes"""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.stop_btn.setEnabled(True)
        else:
            self.stop_btn.setEnabled(False)

    def save_converted_audio(self):
        """Save converted audio"""
        if not self.converted_file:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Converted Audio",
            f"converted_audio_{int(time.time())}.wav",
            "Audio Files (*.wav)",
        )

        if file_path:
            try:
                import shutil

                shutil.copy2(self.converted_file, file_path)
                QMessageBox.information(
                    self, "Success", f"Audio saved to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save audio:\n{str(e)}")
