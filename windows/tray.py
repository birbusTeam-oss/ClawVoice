from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QPixmap, QColor
from PyQt6.QtCore import Qt

def create_tray_icon(color: str = "#6B5ECD") -> QPixmap:
    """Create a simple mic icon as tray indicator"""
    pixmap = QPixmap(16, 16)
    pixmap.fill(QColor(color))
    return pixmap

class TrayManager:
    def __init__(self, app, clawvoice, settings_window):
        self.tray = QSystemTrayIcon()
        self.clawvoice = clawvoice
        self.settings_window = settings_window

        # Default purple icon
        self.icon_idle = QIcon(create_tray_icon("#6B5ECD"))
        self.icon_recording = QIcon(create_tray_icon("#FF4444"))
        self.icon_transcribing = QIcon(create_tray_icon("#FFB300"))

        self.tray.setIcon(self.icon_idle)
        self.tray.setToolTip("ClawVoice — Hold Right Alt to dictate")

        # Context menu
        menu = QMenu()
        menu.addAction("⚙️ Settings", settings_window.show)
        menu.addSeparator()
        menu.addAction("❌ Quit", app.quit)
        self.tray.setContextMenu(menu)

        # Connect status changes
        clawvoice.status_changed.connect(self.on_status_changed)
        clawvoice.transcription_ready.connect(clawvoice.injector.inject)

        self.tray.show()

    def on_status_changed(self, status: str):
        if status == "recording":
            self.tray.setIcon(self.icon_recording)
            self.tray.setToolTip("🔴 ClawVoice — Recording...")
        elif status == "transcribing":
            self.tray.setIcon(self.icon_transcribing)
            self.tray.setToolTip("⏳ ClawVoice — Transcribing...")
        else:
            self.tray.setIcon(self.icon_idle)
            self.tray.setToolTip("ClawVoice — Hold Right Alt to dictate")
