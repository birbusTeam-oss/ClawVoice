from injector import inject
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
import os

def load_icon(name):
    """Load ICO from assets folder"""
    base = os.path.join(os.path.dirname(__file__), "assets", name)
    if os.path.exists(base):
        return QIcon(base)
    # Fallback to bundled path (PyInstaller)
    base2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", name)
    return QIcon(base2)

class TrayManager:
    def __init__(self, app, clawvoice, settings_window):
        self.app = app
        self.tray = QSystemTrayIcon()
        self.clawvoice = clawvoice
        self.settings_window = settings_window

        self.icons = {
            "idle":         load_icon("tray_idle.ico"),
            "recording":    load_icon("tray_recording.ico"),
            "transcribing": load_icon("tray_transcribing.ico"),
            "error":        load_icon("tray_error.ico"),
        }

        self.tray.setIcon(self.icons["idle"])
        self.tray.setToolTip("ClawVoice — Hold Ctrl+Space to dictate")

        menu = QMenu()
        menu.addAction("⚙️ Settings", settings_window.show)
        menu.addSeparator()
        menu.addAction("❌ Quit", app.quit)
        self.tray.setContextMenu(menu)

        clawvoice.status_changed.connect(self._on_status)
        clawvoice.transcription_ready.connect(inject)

        self.tray.show()

    def _on_status(self, status: str):
        icon = self.icons.get(status, self.icons["idle"])
        self.tray.setIcon(icon)
        tooltips = {
            "idle":         "ClawVoice — Hold Ctrl+Space to dictate",
            "recording":    "🔴 Recording... release Ctrl+Space to stop",
            "transcribing": "⏳ Transcribing with Claude...",
            "error":        "⚠️ Check your API key in Settings",
        }
        self.tray.setToolTip(tooltips.get(status, "ClawVoice"))
