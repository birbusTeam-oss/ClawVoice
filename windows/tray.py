import sys
import os
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon


def get_asset_path(filename):
    """Resolve asset path for both dev and PyInstaller frozen bundle."""
    if getattr(sys, 'frozen', False):
        # PyInstaller bundle -- assets are in sys._MEIPASS/assets/
        base = os.path.join(sys._MEIPASS, "assets", filename)
        if os.path.exists(base):
            return base
    # Dev mode -- relative to this file
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", filename)
    return base


class TrayManager:
    def __init__(self, app, clawvoice, settings_window):
        self.app = app
        self.tray = QSystemTrayIcon()
        self.clawvoice = clawvoice
        self.settings_window = settings_window
        self._current_status = "idle"

        self.icons = {
            "idle":         QIcon(get_asset_path("tray_idle.ico")),
            "recording":    QIcon(get_asset_path("tray_recording.ico")),
            "transcribing": QIcon(get_asset_path("tray_transcribing.ico")),
            "error":        QIcon(get_asset_path("tray_error.ico")),
        }

        self.tray.setIcon(self.icons["idle"])
        self.tray.setToolTip("ClawVoice -- Ready")

        menu = QMenu()
        menu.addAction(" Settings", settings_window.show)
        menu.addSeparator()
        menu.addAction("X Quit", app.quit)
        self.tray.setContextMenu(menu)

        clawvoice.status_changed.connect(self._on_status)

        self.tray.show()

    def update_status(self, status: str):
        """Public method to update tray icon and tooltip for a given status."""
        self._on_status(status)

    def _on_status(self, status: str):
        self._current_status = status
        icon = self.icons.get(status, self.icons["idle"])
        self.tray.setIcon(icon)
        tooltips = {
            "idle":         "ClawVoice -- Ready",
            "recording":    "ClawVoice -- Recording... release Ctrl+Alt to stop",
            "transcribing": "ClawVoice -- Transcribing...",
            "error":        "ClawVoice -- Error (see overlay for details)",
        }
        self.tray.setToolTip(tooltips.get(status, "ClawVoice"))
