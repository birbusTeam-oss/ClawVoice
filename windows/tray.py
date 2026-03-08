import sys
import os
from injector import inject
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon


def get_asset_path(filename):
    """Resolve asset path for both dev and PyInstaller frozen bundle."""
    if getattr(sys, 'frozen', False):
        # PyInstaller bundle — assets are in sys._MEIPASS/assets/
        base = os.path.join(sys._MEIPASS, "assets", filename)
        if os.path.exists(base):
            return base
    # Dev mode — relative to this file
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", filename)
    return base


class TrayManager:
    def __init__(self, app, clawvoice, settings_window):
        self.app = app
        self.tray = QSystemTrayIcon()
        self.clawvoice = clawvoice
        self.settings_window = settings_window

        self.icons = {
            "idle":         QIcon(get_asset_path("tray_idle.ico")),
            "recording":    QIcon(get_asset_path("tray_recording.ico")),
            "transcribing": QIcon(get_asset_path("tray_transcribing.ico")),
            "error":        QIcon(get_asset_path("tray_error.ico")),
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
