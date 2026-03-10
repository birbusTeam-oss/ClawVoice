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

# Set up logging so transcriber/main can log
logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("clawvoice")


class SettingsLogHandler(logging.Handler):
    """Routes log messages to the settings window log panel."""
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
    settings = SettingsWindow(config)
    overlay = RecordingOverlay()

    # Route all clawvoice logs to the settings panel
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
            # Always hide overlay when we return to idle or error
            overlay.hide_overlay()

    def on_transcription(text: str):
        word_count = len(text.split())
        overlay.show_success(word_count)

    def on_error(message: str):
        overlay.show_error(message)
        log.error(message)

    clawvoice.status_changed.connect(on_status)
    clawvoice.transcription_ready.connect(inject)
    clawvoice.transcription_ready.connect(on_transcription)
    clawvoice.error_occurred.connect(on_error)

    app.aboutToQuit.connect(clawvoice.shutdown)

    log.info("ClawVoice started — hold Ctrl+Alt to dictate")

    if config.is_first_run():
        settings.show()
    else:
        tray.tray.showMessage("ClawVoice", "Ready — Hold Ctrl+Alt to dictate.", msecs=3000)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
