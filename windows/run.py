"""
ClawVoice for Windows — Entry Point
Run: python run.py
"""
import sys
import keyboard
from PyQt6.QtWidgets import QApplication
from main import ClawVoice
from tray import TrayManager
from settings import SettingsWindow
from config import Config

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Stay alive when settings window closes

    config = Config()
    clawvoice = ClawVoice()
    settings = SettingsWindow(config)

    # Show settings on first run if no API keys configured
    if not config.anthropic_key and not config.openai_key:
        settings.show()

    tray = TrayManager(app, clawvoice, settings)

    print("ClawVoice running. Hold Right Alt to dictate.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
