"""
ClawVoice for Windows — Entry Point
"""
import sys
from PyQt6.QtWidgets import QApplication
from main import ClawVoice
from tray import TrayManager
from settings import SettingsWindow
from overlay import RecordingOverlay
from config import Config

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    config = Config()
    settings = SettingsWindow(config)
    clawvoice = ClawVoice(config)
    overlay = RecordingOverlay()
    tray = TrayManager(app, clawvoice, settings)

    # Connect overlay to status
    def on_status(status):
        if status == "recording":
            overlay.show_recording()
        elif status == "transcribing":
            overlay.show_transcribing()
        else:
            overlay.hide_overlay()

    clawvoice.status_changed.connect(on_status)

    # Show settings on first run
    if not config.anthropic_key:
        settings.show()
    else:
        tray.tray.showMessage("ClawVoice", "Ready! Hold Ctrl+Space to dictate.", msecs=3000)

    print("ClawVoice running. Hold Ctrl+Space to dictate.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
