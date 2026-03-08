from PyQt6.QtWidgets import (QWidget, QVBoxLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt

class SettingsWindow(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowTitle("ClawVoice Settings")
        self.setFixedSize(400, 240)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # API Key group
        api_group = QGroupBox("API Key")
        api_layout = QFormLayout()

        self.anthropic_input = QLineEdit()
        self.anthropic_input.setPlaceholderText("sk-ant-...")
        self.anthropic_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.anthropic_input.setText(self.config.anthropic_key)
        api_layout.addRow("Anthropic (Claude):", self.anthropic_input)

        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        # Info
        info = QLabel("Get your free API key at console.anthropic.com\n\nKeys stored locally. Never sent to any server except Anthropic directly.")
        info.setWordWrap(True)
        info.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(info)

        # Hotkey info
        hotkey_label = QLabel("🎙️ Hold Right Alt anywhere to record")
        hotkey_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(hotkey_label)

        # Save
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        save_btn.setStyleSheet("background: #6B5ECD; color: white; padding: 8px; border-radius: 4px;")
        layout.addWidget(save_btn)

    def save(self):
        self.config.anthropic_key = self.anthropic_input.text()
        self.hide()
