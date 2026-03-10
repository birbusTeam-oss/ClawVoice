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
        elif status == "idle":
            # hide_overlay only if we didn't just show success/error
            # (success/error handle their own auto-hide timers)
            pass
        elif status == "error":
            # overlay error is handled via error_occurred signal with message
            pass

    def on_transcription(text: str):
        # Show success feedback: word count
        word_count = len(text.split())
        overlay.show_success(word_count)
        settings.append_log(f"Transcribed {word_count} words", level="info")

    def on_error(message: str):
        overlay.show_error(message)
        settings.append_log(f"Error: {message}", level="error")

    clawvoice.status_changed.connect(on_status)
    clawvoice.transcription_ready.connect(on_transcription)
    clawvoice.error_occurred.connect(on_error)

    # inject is connected in TrayManager already
    app.aboutToQuit.connect(clawvoice.shutdown)

    settings.append_log("ClawVoice started — ready to dictate")
    tray.tray.showMessage("ClawVoice", "Ready! Hold Ctrl+Alt to dictate.", msecs=3000)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
