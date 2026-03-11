import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QFrame
)
from PyQt6.QtCore import Qt, QDateTime, pyqtSignal


class SettingsWindow(QWidget):
    started = pyqtSignal()  # emitted when user clicks Get Started

    def __init__(self, config, first_run=False, parent=None):
        super().__init__(parent)
        self.config = config
        self._first_run = first_run
        self._log_lines = []
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("ClawVoice")
        self.setMinimumSize(440, 480)
        self.setMaximumWidth(540)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)

        # On first run, prevent closing — user must click Get Started
        if self._first_run:
            self.setWindowFlags(
                Qt.WindowType.Window |
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
            QPushButton#primaryBtn {
                background: #4CAF70;
                color: #000;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: 600;
                min-height: 24px;
            }
            QPushButton#primaryBtn:hover { background: #5ac47e; }
            QPushButton#primaryBtn:pressed { background: #3d9e5f; }
            QPushButton#secondaryBtn {
                background: rgba(255,255,255,0.06);
                color: rgba(255,255,255,0.7);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px;
                padding: 8px 14px;
                font-size: 12px;
                max-width: 110px;
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
            QFrame#divider {
                background: rgba(255,255,255,0.07);
                max-height: 1px;
                min-height: 1px;
                border: none;
            }
        """)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(28, 28, 28, 28)
        self._layout.setSpacing(0)

        if self._first_run:
            self._build_welcome()
        else:
            self._build_dashboard()

    def _build_welcome(self):
        """First-run onboarding screen."""
        layout = self._layout

        title = QLabel("ClawVoice")
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #fff;")
        layout.addWidget(title)
        layout.addSpacing(8)

        sub = QLabel("Voice dictation for Windows")
        sub.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.4);")
        layout.addWidget(sub)
        layout.addSpacing(32)

        # How it works
        steps = [
            ("1.", "Hold  Ctrl + Alt  to start recording"),
            ("2.", "Speak naturally"),
            ("3.", "Release to inject text into any app"),
        ]
        for num, text in steps:
            row = QLabel(f'<span style="color:#4CAF70; font-weight:700;">{num}</span>  {text}')
            row.setStyleSheet("font-size: 13px; color: #e8e8e8; padding: 6px 0;")
            layout.addWidget(row)

        layout.addSpacing(16)

        note = QLabel("Works in any app — browsers, editors, chat, anywhere you type.")
        note.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.3); line-height: 1.4;")
        note.setWordWrap(True)
        layout.addWidget(note)

        layout.addSpacing(32)

        # Get Started button
        btn = QPushButton("Get Started")
        btn.setObjectName("primaryBtn")
        btn.clicked.connect(self._on_get_started)
        layout.addWidget(btn)

        layout.addSpacing(16)

        hint = QLabel("ClawVoice will live in your system tray after setup.")
        hint.setStyleSheet("font-size: 11px; color: rgba(255,255,255,0.25); text-align: center;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        layout.addStretch()

    def _on_get_started(self):
        """User clicked Get Started — switch to dashboard view."""
        self._first_run = False
        # Mark first run complete in config
        self.config.set("setup_complete", True)
        # Allow closing now
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        # Clear and rebuild as dashboard
        self._clear_layout()
        self._build_dashboard()
        self.show()  # re-show after flag change
        self.started.emit()
        # Auto-close after a brief moment so user sees the dashboard transition
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(800, self.hide)

    def _build_dashboard(self):
        """Normal dashboard — profile + logs."""
        layout = self._layout

        title = QLabel("ClawVoice")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #fff;")
        layout.addWidget(title)
        layout.addSpacing(4)

        sub = QLabel("Hold Ctrl+Alt to dictate in any app")
        sub.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.35);")
        layout.addWidget(sub)
        layout.addSpacing(28)

        # Profile
        layout.addWidget(self._section_label("Profile"))
        layout.addSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Display name (optional)")
        saved_name = self.config.get("display_name", "")
        self.name_input.setText(saved_name)
        layout.addWidget(self.name_input)
        layout.addSpacing(8)

        name_btn = QPushButton("Save")
        name_btn.setObjectName("secondaryBtn")
        name_btn.clicked.connect(self._save_name)
        layout.addWidget(name_btn)

        layout.addSpacing(24)
        layout.addWidget(self._divider())
        layout.addSpacing(24)

        # Logs
        layout.addWidget(self._section_label("Logs"))
        layout.addSpacing(10)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMinimumHeight(200)
        self.log_view.setPlaceholderText("Transcription events and errors appear here...")
        layout.addWidget(self.log_view)

        # Replay any logs captured before dashboard was built
        if self._log_lines:
            self.log_view.setHtml("<br>".join(self._log_lines))

        layout.addStretch()

    def _clear_layout(self):
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

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
        if hasattr(self, 'log_view'):
            self.log_view.setHtml("<br>".join(self._log_lines))
            self.log_view.verticalScrollBar().setValue(
                self.log_view.verticalScrollBar().maximum()
            )

    def closeEvent(self, event):
        if self._first_run:
            event.ignore()  # can't close during onboarding
        else:
            self.hide()
            event.ignore()
