# ============ frontend/pyqt_app/main.py ============
import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QStatusBar,
    QMenuBar,
    QMessageBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QFont, QAction

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent / "shared"))
from api_client import VoiceAPIClient

# Import widgets
from widgets.tts_widget import TTSWidget
from widgets.vc_widget import VCWidget


class HealthCheckThread(QThread):
    """Background thread for health checking"""

    health_updated = pyqtSignal(dict)

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.running = True

    def run(self):
        while self.running:
            try:
                health = self.client.health_check()
                self.health_updated.emit(health)
            except Exception as e:
                self.health_updated.emit({"status": "error", "message": str(e)})
            self.msleep(10000)  # Check every 10 seconds

    def stop(self):
        self.running = False


class VoiceAppMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client = VoiceAPIClient()
        self.health_thread = None
        self.init_ui()
        self.setup_styling()
        self.start_health_check()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("🎙️ Voice App - Desktop")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(800, 600)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create menu bar
        self.create_menu_bar()

        # Create status bar
        self.create_status_bar()

        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Create tabs
        self.tts_widget = TTSWidget(self.client)
        self.vc_widget = VCWidget(self.client)

        self.tab_widget.addTab(self.tts_widget, "🎤 Text-to-Speech")
        self.tab_widget.addTab(self.vc_widget, "🎭 Voice Conversion")

        # Connect signals
        self.tts_widget.status_changed.connect(self.update_status)
        self.vc_widget.status_changed.connect(self.update_status)

    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Settings menu
        settings_menu = menubar.addMenu("&Settings")

        theme_action = QAction("&Toggle Theme", self)
        theme_action.triggered.connect(self.toggle_theme)
        settings_menu.addAction(theme_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_status_bar(self):
        """Create status bar with health indicator"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Backend status indicator
        self.backend_status = QLabel("Backend: Checking...")
        self.backend_status.setStyleSheet("QLabel { color: orange; }")
        self.status_bar.addPermanentWidget(self.backend_status)

        # Default message
        self.status_bar.showMessage("Ready")

    def setup_styling(self):
        """Apply custom styling"""
        try:
            # Load theme
            theme_path = Path(__file__).parent / "styles" / "dark_theme.qss"
            if theme_path.exists():
                with open(theme_path, "r") as f:
                    self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Failed to load theme: {e}")

    def start_health_check(self):
        """Start background health checking"""
        self.health_thread = HealthCheckThread(self.client)
        self.health_thread.health_updated.connect(self.update_backend_status)
        self.health_thread.start()

    def update_backend_status(self, health_data):
        """Update backend status indicator"""
        status = health_data.get("status", "unknown")

        if status == "healthy":
            self.backend_status.setText("Backend: ✅ Online")
            self.backend_status.setStyleSheet("QLabel { color: green; }")
        else:
            error_msg = health_data.get("message", "Unknown error")
            self.backend_status.setText(f"Backend: ❌ Offline")
            self.backend_status.setStyleSheet("QLabel { color: red; }")

    def update_status(self, message):
        """Update status bar message"""
        self.status_bar.showMessage(message, 5000)  # Show for 5 seconds

    def toggle_theme(self):
        """Toggle between dark and light theme"""
        # This would switch between theme files
        QMessageBox.information(self, "Theme", "Theme switching not implemented yet")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Voice App",
            "Voice App Desktop v1.0\n\n"
            "Personal Voice Synthesis & Conversion Tool\n"
            "Built with PyQt6 and FastAPI\n\n"
            "Features:\n"
            "• Text-to-Speech (TTS)\n"
            "• Voice Conversion (VC)\n"
            "• Drag & Drop Support\n"
            "• Offline Caching",
        )

    def closeEvent(self, event):
        """Handle application close"""
        if self.health_thread:
            self.health_thread.stop()
            self.health_thread.wait(1000)
        event.accept()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Voice App")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Voice App Team")

    # Create and show main window
    window = VoiceAppMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
