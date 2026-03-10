"""
ClawVoice for Windows — Entry Point
"""
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from main import ClawVoice
from tray import TrayManager
from settings import SettingsWindow
from overlay import RecordingOverlay
from config import Config
from injector import inject


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

    def on_status(status):
        tray.update_status(status)
        if status == "recording":
            overlay.show_recording()
        elif status == "transcribing":
            overlay.show_transcribing()

    def on_transcription(text: str):
        word_count = len(text.split())
        overlay.show_success(word_count)
        settings.append_log(f"Transcribed {word_count} words")

    def on_error(message: str):
        overlay.show_error(message)
        settings.append_log(f"Error: {message}", level="error")

    clawvoice.status_changed.connect(on_status)
    clawvoice.transcription_ready.connect(inject)
    clawvoice.transcription_ready.connect(on_transcription)
    clawvoice.error_occurred.connect(on_error)

    app.aboutToQuit.connect(clawvoice.shutdown)

    settings.append_log("ClawVoice started — hold Ctrl+Alt to dictate")

    # Always show settings on first launch so user knows it's running
    if config.is_first_run():
        settings.show()
    else:
        tray.tray.showMessage("ClawVoice", "Ready — Hold Ctrl+Alt to dictate.", msecs=3000)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
