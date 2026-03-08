from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter
from PyQt6.QtCore import Qt
import os

def make_color_icon(color: str) -> QIcon:
    pixmap = QPixmap(22, 22)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(color))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(1, 1, 20, 20)
    painter.end()
    return QIcon(pixmap)

class TrayManager:
    def __init__(self, app, clawvoice, settings_window):
        self.app = app
        self.tray = QSystemTrayIcon()
        self.clawvoice = clawvoice
        self.settings_window = settings_window

        self.icons = {
            "idle":        make_color_icon("#6B5ECD"),   # purple
            "recording":   make_color_icon("#E05555"),   # red
            "transcribing":make_color_icon("#F0A500"),   # amber
            "error":       make_color_icon("#888888"),   # grey
        }

        self.tray.setIcon(self.icons["idle"])
        self.tray.setToolTip("ClawVoice — Hold Right Alt to dictate")

        menu = QMenu()
        menu.addAction("⚙️ Settings", settings_window.show)
        menu.addSeparator()
        menu.addAction("❌ Quit", app.quit)
        self.tray.setContextMenu(menu)

        clawvoice.status_changed.connect(self._on_status)
        clawvoice.transcription_ready.connect(clawvoice.injector.inject)

        self.tray.show()

    def _on_status(self, status: str):
        icon = self.icons.get(status, self.icons["idle"])
        self.tray.setIcon(icon)
        tooltips = {
            "idle": "ClawVoice — Hold Right Alt to dictate",
            "recording": "🔴 Recording... release Right Alt to stop",
            "transcribing": "⏳ Transcribing with Claude...",
            "error": "⚠️ ClawVoice — check your API key in Settings",
        }
        self.tray.setToolTip(tooltips.get(status, "ClawVoice"))
