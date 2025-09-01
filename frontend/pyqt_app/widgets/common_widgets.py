from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class StatusCard(QWidget):
    """Reusable status display card"""

    def __init__(self, title, value="", icon=""):
        super().__init__()
        self.init_ui(title, value, icon)

    def init_ui(self, title, value, icon):
        layout = QHBoxLayout(self)

        # Icon
        if icon:
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Arial", 16))
            layout.addWidget(icon_label)

        # Content
        content_layout = QVBoxLayout()

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-weight: bold; color: #6b7280;")
        content_layout.addWidget(self.title_label)

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        content_layout.addWidget(self.value_label)

        layout.addLayout(content_layout)
        layout.addStretch()

    def update_value(self, value):
        """Update the displayed value"""
        self.value_label.setText(str(value))
