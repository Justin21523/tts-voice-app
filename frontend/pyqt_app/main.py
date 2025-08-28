from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit
import sys
from shared.api_client import tts
class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TTS Voice App")
        l=QVBoxLayout(self)
        self.input=QTextEdit(); l.addWidget(self.input)
        btn=QPushButton("Synthesize"); l.addWidget(btn)
        btn.clicked.connect(self.run)
    def run(self):
        print(tts(self.input.toPlainText()))
if __name__ == "__main__":
    app=QApplication(sys.argv); w=Main(); w.show(); sys.exit(app.exec())
