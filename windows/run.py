"""
ClawVoice for Windows — Entry Point
No welcome screen. Starts silently, lives in tray.
"""
import sys
import os
import logging
import traceback

_log_dir = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "ClawVoice")
os.makedirs(_log_dir, exist_ok=True)
_log_file = os.path.join(_log_dir, "clawvoice.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(_log_file, mode='a', encoding='utf-8'),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger("clawvoice")
log.info("=== ClawVoice starting ===")


def _global_exception_hook(exc_type, exc_value, exc_tb):
    try:
        log.error(f"UNHANDLED CRASH: {exc_type.__name__}: {exc_value}")
        log.error("".join(traceback.format_exception(exc_type, exc_value, exc_tb)))
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
            # Only show errors in the UI — status/info goes to file log only
            if record.levelno >= logging.ERROR:
                self.settings.append_log(record.getMessage(), level="error")
        except Exception:
            pass


def safe_inject(text: str):
    try:
        log.info("Injecting text...")
        from injector import inject
        inject(text)
        log.info("Inject complete")
    except Exception as e:
        log.error(f"Inject failed: {e}")


def warmup():
    try:
        import speech_recognition as sr
        sr.Recognizer()
        log.info("WARMUP: speech engine OK")
    except Exception as e:
        log.error(f"WARMUP: speech failed: {e}")

    try:
        import pyperclip
        pyperclip.paste()
        log.info("WARMUP: clipboard OK")
    except Exception:
        pass

    try:
        import pyaudio
        pa = pyaudio.PyAudio()
        try:
            info = pa.get_default_input_device_info()
            log.info(f"WARMUP: mic '{info['name']}' rate={int(info['defaultSampleRate'])}")
        except Exception:
            log.info("WARMUP: no default mic found")
        pa.terminate()
    except Exception as e:
        log.error(f"WARMUP: audio failed: {e}")

    try:
        from pynput.keyboard import Controller
        Controller()
        log.info("WARMUP: keyboard controller OK")
    except Exception as e:
        log.error(f"WARMUP: controller failed: {e}")


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("ClawVoice")
    log.info("Qt app created")

    from config import Config
    from settings import SettingsWindow
    from overlay import RecordingOverlay
    from tray import TrayManager
    from main import ClawVoice

    config = Config()
    config.set("setup_complete", True)

    # Auto-enable Start with Windows on first install
    if not config.get("startup_configured", False):
        config.set("startup_configured", True)
        config.set("start_with_windows", True)
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            import sys as _sys
            exe = _sys.executable if getattr(_sys, 'frozen', False) else os.path.abspath(_sys.argv[0])
            winreg.SetValueEx(key, "ClawVoice", 0, winreg.REG_SZ, f'"{exe}"')
            winreg.CloseKey(key)
            log.info("Start with Windows enabled (default)")
        except Exception as e:
            log.error(f"Startup registry: {e}")

    settings = SettingsWindow(config, first_run=False)
    overlay = RecordingOverlay()

    log.addHandler(SettingsLogHandler(settings))

    try:
        clawvoice = ClawVoice(config)
        log.info("ClawVoice engine created")
    except Exception as e:
        log.error(f"Engine failed: {e}")
        QMessageBox.critical(None, "ClawVoice",
            f"Failed to start: {e}\n\nTry running as Administrator.")
        sys.exit(1)

    warmup()
    log.info("Warmup complete")

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
            log.error(f"Status: {e}")

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
        except Exception:
            pass

    def start_listening_now():
        log.info("Starting hotkey listener...")
        clawvoice.start_listening()
        log.info("Hotkey listener active — Ctrl+Alt ready")
        tray.tray.showMessage(
            "ClawVoice",
            "Ready — Hold Ctrl+Alt to dictate anywhere.",
            msecs=4000
        )

    clawvoice.status_changed.connect(on_status)
    clawvoice.transcription_ready.connect(safe_inject)
    clawvoice.transcription_ready.connect(on_transcription)
    clawvoice.error_occurred.connect(on_error)
    app.aboutToQuit.connect(clawvoice.shutdown)

    keepalive = QTimer()
    keepalive.timeout.connect(lambda: None)
    keepalive.start(5000)

    # Show "Initializing..." notification, then start listener after 1.5s
    tray.tray.showMessage("ClawVoice", "Initializing...", msecs=2000)
    QTimer.singleShot(1500, start_listening_now)

    log.info("ClawVoice starting up — no window, tray only")
    app.exec()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.error(f"FATAL: {e}")
        traceback.print_exc()
