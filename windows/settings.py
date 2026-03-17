import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QFrame, QCheckBox
)
from PyQt6.QtCore import Qt, QDateTime, pyqtSignal


class SettingsWindow(QWidget):
    started = pyqtSignal()
    _log_signal = pyqtSignal(str, str)

    def __init__(self, config, first_run=False, parent=None):
        super().__init__(parent)
        self.config = config
        self._first_run = first_run
        self._log_lines = []
        self._log_signal.connect(self._append_log_main_thread)
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("ClawVoice")
        self.setMinimumSize(440, 460)
        self.setMaximumWidth(540)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        # Normal window -- always has close button, no flag tricks
        self.setStyleSheet("""
            QWidget {
                background: #0f0f0f;
                color: #e8e8e8;
                font-family: 'Segoe UI', sans-serif;
            }
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
            QCheckBox {
                font-size: 13px;
                color: #e8e8e8;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px; height: 16px;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 3px;
                background: #1a1a1a;
            }
            QCheckBox::indicator:checked {
                background: #4CAF70;
                border-color: #4CAF70;
            }
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
                max-height: 1px; min-height: 1px; border: none;
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
        layout = self._layout

        title = QLabel("ClawVoice")
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #fff;")
        layout.addWidget(title)
        layout.addSpacing(8)

        sub = QLabel("Voice dictation for Windows")
        sub.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.4);")
        layout.addWidget(sub)
        layout.addSpacing(32)

        for num, text in [("1.", "Hold  Ctrl + Alt  to start recording"),
                          ("2.", "Speak naturally"),
                          ("3.", "Release to inject text into any app")]:
            row = QLabel(f'<span style="color:#4CAF70; font-weight:700;">{num}</span>  {text}')
            row.setStyleSheet("font-size: 13px; color: #e8e8e8; padding: 6px 0;")
            layout.addWidget(row)

        layout.addSpacing(16)

        note = QLabel("Works in any app -- browsers, editors, chat, anywhere you type.")
        note.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.3);")
        note.setWordWrap(True)
        layout.addWidget(note)

        layout.addSpacing(32)

        btn = QPushButton("Get Started")
        btn.setObjectName("primaryBtn")
        btn.clicked.connect(self._on_get_started)
        layout.addWidget(btn)

        layout.addSpacing(16)

        hint = QLabel("ClawVoice will live in your system tray.")
        hint.setStyleSheet("font-size: 11px; color: rgba(255,255,255,0.25);")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        layout.addStretch()

    def _on_get_started(self):
        self._first_run = False
        self.config.set("setup_complete", True)
        # Just swap layouts -- NO window flag changes, NO self.show()
        self._clear_layout()
        self._build_dashboard()
        self.started.emit()
        # Hide after a moment
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1500, self.hide)

    def _build_dashboard(self):
        layout = self._layout

        title = QLabel("ClawVoice")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #fff;")
        layout.addWidget(title)
        layout.addSpacing(4)

        sub = QLabel("Hold Ctrl+Alt to dictate in any app")
        sub.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.35);")
        layout.addWidget(sub)
        layout.addSpacing(24)

        layout.addWidget(self._section_label("Settings"))
        layout.addSpacing(12)

        self.startup_check = QCheckBox("Start with Windows")
        self.startup_check.setChecked(self.config.get("start_with_windows", True))
        self.startup_check.toggled.connect(self._toggle_startup)
        layout.addWidget(self.startup_check)
        layout.addSpacing(8)

        self.log_transcriptions_check = QCheckBox("Log transcriptions (local only)")
        self.log_transcriptions_check.setChecked(self.config.get("log_transcriptions", False))
        self.log_transcriptions_check.toggled.connect(
            lambda checked: self.config.set("log_transcriptions", checked)
        )
        layout.addWidget(self.log_transcriptions_check)

        layout.addSpacing(20)
        layout.addWidget(self._divider())
        layout.addSpacing(20)

        layout.addWidget(self._section_label("Logs"))
        layout.addSpacing(4)

        log_hint = QLabel("Errors always logged. Transcriptions logged when enabled above.")
        log_hint.setStyleSheet("font-size: 11px; color: rgba(255,255,255,0.2); margin-bottom: 8px;")
        layout.addWidget(log_hint)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMinimumHeight(220)
        self.log_view.setPlaceholderText("Errors and events appear here...")
        layout.addWidget(self.log_view)

        if self._log_lines:
            self.log_view.setHtml("<br>".join(self._log_lines))

        layout.addStretch()

    def _toggle_startup(self, checked):
        self.config.set("start_with_windows", checked)
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            if checked:
                import sys, os
                exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
                winreg.SetValueEx(key, "ClawVoice", 0, winreg.REG_SZ, f'"{exe_path}"')
                self.append_log("Start with Windows enabled")
            else:
                try:
                    winreg.DeleteValue(key, "ClawVoice")
                except FileNotFoundError:
                    pass
                self.append_log("Start with Windows disabled")
            winreg.CloseKey(key)
        except Exception as e:
            self.append_log(f"Registry error: {e}", level="error")

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

    def append_log(self, message, level="info"):
        self._log_signal.emit(message, level)

    def _append_log_main_thread(self, message, level):
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        color_map = {"error": "#ef4444", "warn": "#F59E0B", "info": "rgba(255,255,255,0.4)"}
        color = color_map.get(level, color_map["info"])
        self._log_lines.append(
            f'<span style="color:rgba(255,255,255,0.2)">[{timestamp}]</span> '
            f'<span style="color:{color}">{message}</span>'
        )
        if hasattr(self, 'log_view'):
            self.log_view.setHtml("<br>".join(self._log_lines))
            self.log_view.verticalScrollBar().setValue(
                self.log_view.verticalScrollBar().maximum()
            )

    def should_log_transcriptions(self):
        return self.config.get("log_transcriptions", False)

    def closeEvent(self, event):
        self.hide()
        event.ignore()
