"""
ClawVoice for Windows — Entry Point
"""
import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from main import ClawVoice
from tray import TrayManager
from settings import SettingsWindow
from overlay import RecordingOverlay
from config import Config


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("ClawVoice")

    config = Config()
    settings = SettingsWindow(config)
    overlay = RecordingOverlay()

    try:
        clawvoice = ClawVoice(config)
    except Exception as e:
        QMessageBox.critical(None, "ClawVoice",
            f"Failed to start: {e}\n\nTry running as Administrator.")
        sys.exit(1)

    tray = TrayManager(app, clawvoice, settings)

    # Connect overlay to status changes
    def on_status(status):
        if status == "recording":
            overlay.show_recording()
        elif status == "transcribing":
            overlay.show_transcribing()
        else:
            overlay.hide_overlay()

    clawvoice.status_changed.connect(on_status)

    # Show settings on first run (no API key yet)
    if not config.anthropic_key:
        settings.show()
    else:
        tray.tray.showMessage("ClawVoice", "Ready! Hold Ctrl+Space to dictate.", msecs=3000)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
