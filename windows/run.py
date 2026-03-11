"""
ClawVoice for Windows — Entry Point
Crash-resilient: stays running no matter what.
"""
import sys
import logging
import traceback

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("clawvoice")


def _global_exception_hook(exc_type, exc_value, exc_tb):
    """Catch unhandled exceptions — log them, don't crash."""
    try:
        log.error(f"Unhandled: {exc_type.__name__}: {exc_value}")
    except Exception:
        pass

sys.excepthook = _global_exception_hook

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer


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
    """Crash-safe inject wrapper."""
    try:
        from injector import inject
        inject(text)
    except Exception as e:
        log.error(f"Inject failed: {e}")


def warmup():
    """Pre-load all heavy dependencies so first real use is instant."""
    try:
        # 1. Pre-load SpeechRecognition + FLAC encoder
        import speech_recognition as sr
        r = sr.Recognizer()
        r.energy_threshold = 300
        log.info("Speech engine loaded")
    except Exception as e:
        log.error(f"Speech warmup: {e}")

    try:
        # 2. Pre-load pynput Controller (AFTER keyboard hook is set up)
        from injector import _get_controller
        _get_controller()
        log.info("Input controller loaded")
    except Exception as e:
        log.error(f"Controller warmup: {e}")

    try:
        # 3. Pre-load pyperclip
        import pyperclip
        pyperclip.paste()
    except Exception:
        pass

    try:
        # 4. Pre-init PyAudio
        import pyaudio
        pa = pyaudio.PyAudio()
        pa.terminate()
        log.info("Audio system loaded")
    except Exception as e:
        log.error(f"Audio warmup: {e}")


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("ClawVoice")

    from config import Config
    from settings import SettingsWindow
    from overlay import RecordingOverlay
    from tray import TrayManager
    from main import ClawVoice

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

    # Warmup AFTER keyboard hook is set up (important: pynput must init after keyboard)
    warmup()

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
            if settings.should_log_transcriptions():
                log.info(f"[{word_count} words] {text}")
        except Exception as e:
            log.error(f"Display: {e}")

    def on_error(message: str):
        try:
            overlay.show_error(message)
        except Exception as e:
            log.error(f"Error display: {e}")

    def on_started():
        tray.tray.showMessage(
            "ClawVoice",
            "Running in background — Hold Ctrl+Alt to dictate anywhere.",
            msecs=5000
        )
        log.info("Ready — hold Ctrl+Alt to dictate")

    clawvoice.status_changed.connect(on_status)
    clawvoice.transcription_ready.connect(safe_inject)
    clawvoice.transcription_ready.connect(on_transcription)
    clawvoice.error_occurred.connect(on_error)
    settings.started.connect(on_started)

    app.aboutToQuit.connect(clawvoice.shutdown)

    # Keepalive — prevents event loop from exiting
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


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal: {e}")
        traceback.print_exc()
