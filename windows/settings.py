import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QFrame
)
from PyQt6.QtCore import Qt, QDateTime


class SettingsWindow(QWidget):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self._log_lines = []
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("ClawVoice")
        self.setMinimumSize(440, 480)
        self.setMaximumWidth(540)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)

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
                background: rgba(255,255,255,0.06);
                color: rgba(255,255,255,0.7);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px;
                padding: 8px 14px;
                font-size: 12px;
                max-width: 110px;
            }
            QPushButton#saveBtn:hover { background: rgba(255,255,255,0.1); }
            QTextEdit {
                background: #111;
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
                color: rgba(255,255,255,0.5);
            }
            QFrame#divider {
                background: rgba(255,255,255,0.07);
                max-height: 1px;
                min-height: 1px;
                border: none;
            }
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 28, 28, 28)
        outer.setSpacing(0)

        # Header
        title = QLabel("ClawVoice")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #fff;")
        outer.addWidget(title)
        outer.addSpacing(4)

        sub = QLabel("Hold Ctrl+Alt to dictate in any app")
        sub.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.35);")
        outer.addWidget(sub)
        outer.addSpacing(28)

        # Profile section
        outer.addWidget(self._section_label("Profile"))
        outer.addSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Display name (optional)")
        saved_name = self.config.get("display_name", "")
        self.name_input.setText(saved_name)
        outer.addWidget(self.name_input)
        outer.addSpacing(8)

        name_btn = QPushButton("Save")
        name_btn.setObjectName("saveBtn")
        name_btn.clicked.connect(self._save_name)
        outer.addWidget(name_btn)

        outer.addSpacing(24)
        outer.addWidget(self._divider())
        outer.addSpacing(24)

        # Logs section
        outer.addWidget(self._section_label("Logs"))
        outer.addSpacing(10)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMinimumHeight(200)
        self.log_view.setPlaceholderText("Transcription events and errors appear here...")
        outer.addWidget(self.log_view)

        outer.addStretch()

    def _section_label(self, text):
        label = QLabel(text.upper())
        label.setStyleSheet("font-size: 10px; font-weight: 600; color: rgba(255,255,255,0.3); letter-spacing: 1px;")
        return label

    def _divider(self):
        f = QFrame()
        f.setObjectName("divider")
        f.setFrameShape(QFrame.Shape.HLine)
        return f

    def _save_name(self):
        name = self.name_input.text().strip()
        self.config.set("display_name", name)
        self.append_log(f"Name saved: {name or '(cleared)'}")

    def append_log(self, message, level="info"):
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        color = {"error": "#ef4444", "warn": "#F59E0B"}.get(level, "rgba(255,255,255,0.45)")
        self._log_lines.append(
            f'<span style="color:rgba(255,255,255,0.25)">[{timestamp}]</span> '
            f'<span style="color:{color}">{message}</span>'
        )
        self.log_view.setHtml("<br>".join(self._log_lines))
        self.log_view.verticalScrollBar().setValue(
            self.log_view.verticalScrollBar().maximum()
        )

    def closeEvent(self, event):
        self.hide()
        event.ignore()
