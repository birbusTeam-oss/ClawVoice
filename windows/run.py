"""
ClawVoice for Windows — Entry Point
"""
import sys
import logging
from PyQt6.QtWidgets import QApplication, QMessageBox
from main import ClawVoice
from tray import TrayManager
from settings import SettingsWindow
from overlay import RecordingOverlay
from config import Config
from injector import inject

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("clawvoice")


class SettingsLogHandler(logging.Handler):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings

    def emit(self, record):
        level = "error" if record.levelno >= logging.ERROR else "info"
        try:
            self.settings.append_log(record.getMessage(), level=level)
        except Exception:
            pass


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("ClawVoice")

    config = Config()
    first_run = not config.get("setup_complete", False)
    settings = SettingsWindow(config, first_run=first_run)
    overlay = RecordingOverlay()

    log.addHandler(SettingsLogHandler(settings))

    try:
        clawvoice = ClawVoice(config)
    except Exception as e:
        QMessageBox.critical(None, "ClawVoice",
            f"Failed to start: {e}\n\nTry running as Administrator.")
        sys.exit(1)

    tray = TrayManager(app, clawvoice, settings)

    def on_status(status):
        tray.update_status(status)
        if status == "recording":
            overlay.show_recording()
        elif status == "transcribing":
            overlay.show_transcribing()
        elif status in ("idle", "error"):
            overlay.hide_overlay()

    def on_transcription(text: str):
        word_count = len(text.split())
        overlay.show_success(word_count)

    def on_error(message: str):
        overlay.show_error(message)
        log.error(message)

    def on_started():
        tray.tray.showMessage("ClawVoice", "Ready — Hold Ctrl+Alt to dictate.", msecs=3000)
        log.info("ClawVoice ready — hold Ctrl+Alt to dictate")

    clawvoice.status_changed.connect(on_status)
    clawvoice.transcription_ready.connect(inject)
    clawvoice.transcription_ready.connect(on_transcription)
    clawvoice.error_occurred.connect(on_error)
    settings.started.connect(on_started)

    app.aboutToQuit.connect(clawvoice.shutdown)

    if first_run:
        settings.show()
        settings.raise_()
        settings.activateWindow()
    else:
        log.info("ClawVoice started — hold Ctrl+Alt to dictate")
        tray.tray.showMessage("ClawVoice", "Ready — Hold Ctrl+Alt to dictate.", msecs=3000)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
