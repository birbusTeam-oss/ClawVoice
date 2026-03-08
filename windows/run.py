"""
ClawVoice for Windows — Entry Point
"""
import sys
from PyQt6.QtWidgets import QApplication
from main import ClawVoice
from tray import TrayManager
from settings import SettingsWindow
from config import Config

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    config = Config()
    settings = SettingsWindow(config)
    clawvoice = ClawVoice(config)  # pass shared config
    tray = TrayManager(app, clawvoice, settings)

    # Show settings on first run
    if not config.anthropic_key:
        settings.show()
    else:
        tray.tray.showMessage(
            "ClawVoice",
            "Running! Hold Right Alt anywhere to dictate.",
            msecs=3000
        )

    print("ClawVoice running. Hold Right Alt to dictate.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
