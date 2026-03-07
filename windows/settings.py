from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt

class SettingsWindow(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowTitle("ClawVoice Settings")
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # API Keys group
        api_group = QGroupBox("API Keys")
        api_layout = QFormLayout()

        self.anthropic_input = QLineEdit()
        self.anthropic_input.setPlaceholderText("sk-ant-...")
        self.anthropic_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.anthropic_input.setText(self.config.anthropic_key)
        api_layout.addRow("Anthropic (Claude):", self.anthropic_input)

        self.openai_input = QLineEdit()
        self.openai_input.setPlaceholderText("sk-...")
        self.openai_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_input.setText(self.config.openai_key)
        api_layout.addRow("OpenAI (Whisper):", self.openai_input)

        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        # Info label
        info = QLabel("💡 Keys stored locally on your machine. Never sent to any server except Anthropic/OpenAI directly.")
        info.setWordWrap(True)
        info.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(info)

        # Hotkey info
        hotkey_label = QLabel("🎙️ Hotkey: Hold Right Alt to record, release to transcribe")
        hotkey_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(hotkey_label)

        # Save button
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        save_btn.setStyleSheet("background: #6B5ECD; color: white; padding: 8px; border-radius: 4px;")
        layout.addWidget(save_btn)

    def save(self):
        self.config.anthropic_key = self.anthropic_input.text()
        self.config.openai_key = self.openai_input.text()
        self.hide()
