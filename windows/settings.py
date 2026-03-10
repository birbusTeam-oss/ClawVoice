import os
import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QFont, QColor


class SettingsWindow(QWidget):
    def __init__(self, config, required=False, parent=None):
        super().__init__(parent)
        self.config = config
        self.required = required
        self._log_lines = []
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("ClawVoice")
        self.setMinimumSize(460, 560)
        self.setMaximumWidth(560)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)

        if self.required:
            self.setWindowFlags(
                Qt.WindowType.Window |
                Qt.WindowType.CustomizeWindowHint |
                Qt.WindowType.WindowTitleHint |
                Qt.WindowType.WindowMinimizeButtonHint
            )

        self.setStyleSheet("""
            QWidget {
                background: #0f0f0f;
                color: #e8e8e8;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit {
                background: #1a1a1a;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 13px;
                color: #e8e8e8;
                min-height: 20px;
            }
            QLineEdit:focus { border-color: #4CAF70; }
            QPushButton#saveBtn {
                background: #4CAF70;
                color: #000;
                border: none;
                border-radius: 6px;
                padding: 11px;
                font-size: 13px;
                font-weight: 600;
                min-height: 20px;
            }
            QPushButton#saveBtn:hover { background: #5ac47e; }
            QPushButton#saveBtn:pressed { background: #3d9e5f; }
            QPushButton#secondaryBtn {
                background: rgba(255,255,255,0.06);
                color: rgba(255,255,255,0.7);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px;
                padding: 8px 14px;
                font-size: 12px;
            }
            QPushButton#secondaryBtn:hover { background: rgba(255,255,255,0.1); }
            QTextEdit {
                background: #111;
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
                color: rgba(255,255,255,0.5);
            }
            QLabel#sectionLabel {
                font-size: 10px;
                font-weight: 600;
                color: rgba(255,255,255,0.3);
                letter-spacing: 1px;
            }
            QLabel#statusLabel { font-size: 12px; padding: 4px 0; }
            QFrame#divider {
                background: rgba(255,255,255,0.07);
                max-height: 1px;
                min-height: 1px;
            }
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 28, 28, 28)
        outer.setSpacing(0)

        title = QLabel("ClawVoice")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #fff; margin-bottom: 4px;")
        outer.addWidget(title)

        sub = QLabel("Hold Ctrl+Alt to dictate in any app")
        sub.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.35); margin-bottom: 24px;")
        outer.addWidget(sub)

        # API Section
        outer.addWidget(self._section_label("API Key"))
        outer.addSpacing(8)

        current_key = self.config.get_api_key() or ""
        masked = f"sk-ant-...{current_key[-6:]}" if len(current_key) > 10 else ("Not set" if not current_key else current_key)

        self.key_status = QLabel(f"Current: {masked}")
        self.key_status.setObjectName("statusLabel")
        self.key_status.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.4); margin-bottom: 8px;")
        outer.addWidget(self.key_status)

        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("Paste new Anthropic API key...")
        self.api_input.setEchoMode(QLineEdit.EchoMode.Password)
        outer.addWidget(self.api_input)
        outer.addSpacing(8)

        self.validation_label = QLabel("")
        self.validation_label.setObjectName("statusLabel")
        self.validation_label.setStyleSheet("font-size: 12px;")
        self.validation_label.hide()
        outer.addWidget(self.validation_label)

        save_btn = QPushButton("Save API Key")
        save_btn.setObjectName("saveBtn")
        save_btn.clicked.connect(self._save_key)
        outer.addWidget(save_btn)

        outer.addSpacing(24)
        outer.addWidget(self._divider())
        outer.addSpacing(24)

        # Profile Section
        outer.addWidget(self._section_label("Profile"))
        outer.addSpacing(8)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Display name (optional)")
        saved_name = self.config.get("display_name", "") if hasattr(self.config, 'get') else ""
        self.name_input.setText(saved_name)
        outer.addWidget(self.name_input)
        outer.addSpacing(8)

        name_btn = QPushButton("Save Name")
        name_btn.setObjectName("secondaryBtn")
        name_btn.clicked.connect(self._save_name)
        name_btn.setMaximumWidth(110)
        outer.addWidget(name_btn)

        outer.addSpacing(24)
        outer.addWidget(self._divider())
        outer.addSpacing(24)

        # Logs Section
        outer.addWidget(self._section_label("Logs"))
        outer.addSpacing(8)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMinimumHeight(140)
        self.log_view.setMaximumHeight(200)
        self.log_view.setPlaceholderText("Transcription events and errors appear here...")
        outer.addWidget(self.log_view)

        outer.addStretch()

    def _section_label(self, text):
        label = QLabel(text.upper())
        label.setObjectName("sectionLabel")
        label.setStyleSheet("font-size: 10px; font-weight: 600; color: rgba(255,255,255,0.3); letter-spacing: 1px;")
        return label

    def _divider(self):
        f = QFrame()
        f.setObjectName("divider")
        f.setFrameShape(QFrame.Shape.HLine)
        f.setStyleSheet("background: rgba(255,255,255,0.07); border: none; max-height: 1px;")
        return f

    def _save_key(self):
        key = self.api_input.text().strip()
        if not key:
            self._show_validation("Enter an API key first", error=True)
            return
        if not self.config.is_valid_key(key):
            self._show_validation("Invalid key format — should start with sk-ant-", error=True)
            return
        self.config.set_api_key(key)
        masked = f"sk-ant-...{key[-6:]}"
        self.key_status.setText(f"Current: {masked}")
        self.api_input.clear()
        self._show_validation("API key saved", error=False)
        self.append_log("API key updated")
        if self.required:
            self.required = False
            self.setWindowFlags(
                Qt.WindowType.Window |
                Qt.WindowType.CustomizeWindowHint |
                Qt.WindowType.WindowTitleHint |
                Qt.WindowType.WindowMinimizeButtonHint |
                Qt.WindowType.WindowCloseButtonHint
            )
            self.show()

    def _save_name(self):
        name = self.name_input.text().strip()
        if hasattr(self.config, 'set'):
            self.config.set("display_name", name)
        self.append_log(f"Display name set: {name or '(cleared)'}")

    def _show_validation(self, msg, error=True):
        self.validation_label.setText(msg)
        color = "#ef4444" if error else "#4CAF70"
        self.validation_label.setStyleSheet(f"font-size: 12px; color: {color};")
        self.validation_label.show()

    def append_log(self, message, level="info"):
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        color = {"error": "#ef4444", "warn": "#F59E0B", "info": "rgba(255,255,255,0.45)"}.get(level, "rgba(255,255,255,0.45)")
        self._log_lines.append(f'<span style="color:rgba(255,255,255,0.25)">[{timestamp}]</span> <span style="color:{color}">{message}</span>')
        self.log_view.setHtml("<br>".join(self._log_lines[-50:]))
        self.log_view.verticalScrollBar().setValue(self.log_view.verticalScrollBar().maximum())

    def set_required(self, required):
        self.required = required
        if required:
            self.setWindowFlags(
                Qt.WindowType.Window |
                Qt.WindowType.CustomizeWindowHint |
                Qt.WindowType.WindowTitleHint |
                Qt.WindowType.WindowMinimizeButtonHint
            )
            self.show()

    def closeEvent(self, event):
        if self.required:
            event.ignore()
        else:
            self.hide()
            event.ignore()
