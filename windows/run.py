"""
ClawVoice for Windows — Entry Point
Crash-resilient: stays running no matter what.
"""
import sys
import logging
import traceback

# Global exception hook — prevents unhandled exceptions from killing the app
def _global_exception_hook(exc_type, exc_value, exc_tb):
    log.error(f"Unhandled: {exc_type.__name__}: {exc_value}")
    log.error(traceback.format_exception(exc_type, exc_value, exc_tb)[-1].strip())

sys.excepthook = _global_exception_hook

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from main import ClawVoice
from tray import TrayManager
from settings import SettingsWindow
from overlay import RecordingOverlay
from config import Config

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("clawvoice")


class SettingsLogHandler(logging.Handler):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings

    def emit(self, record):
        try:
            level = "error" if record.levelno >= logging.ERROR else "info"
            self.settings.append_log(record.getMessage(), level=level)
        except Exception:
            pass


def safe_inject(text: str):
    """Crash-safe wrapper around inject. Never lets the app die."""
    try:
        from injector import inject
        inject(text)
    except Exception as e:
        log.error(f"Inject failed: {e}")


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
        try:
            tray.update_status(status)
            if status == "recording":
                overlay.show_recording()
            elif status == "transcribing":
                overlay.show_transcribing()
            elif status in ("idle", "error"):
                overlay.hide_overlay()
        except Exception as e:
            log.error(f"Status handler: {e}")

    def on_transcription(text: str):
        try:
            word_count = len(text.split())
            overlay.show_success(word_count)
        except Exception as e:
            log.error(f"Transcription display: {e}")

    def on_error(message: str):
        try:
            overlay.show_error(message)
            log.error(message)
        except Exception as e:
            log.error(f"Error handler: {e}")

    def on_started():
        tray.tray.showMessage("ClawVoice", "Ready — Hold Ctrl+Alt to dictate.", msecs=3000)
        log.info("ClawVoice ready — hold Ctrl+Alt to dictate")

    clawvoice.status_changed.connect(on_status)
    clawvoice.transcription_ready.connect(safe_inject)
    clawvoice.transcription_ready.connect(on_transcription)
    clawvoice.error_occurred.connect(on_error)
    settings.started.connect(on_started)

    app.aboutToQuit.connect(clawvoice.shutdown)

    # Keepalive timer — prevents the event loop from exiting unexpectedly
    keepalive = QTimer()
    keepalive.timeout.connect(lambda: None)
    keepalive.start(5000)

    if first_run:
        settings.show()
        settings.raise_()
        settings.activateWindow()
    else:
        log.info("ClawVoice started — hold Ctrl+Alt to dictate")
        tray.tray.showMessage("ClawVoice", "Ready — Hold Ctrl+Alt to dictate.", msecs=3000)

    app.exec()
    # Don't sys.exit — just let main() return naturally


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal: {e}")
        traceback.print_exc()
