"""
ClawVoice for Windows — Hold Ctrl+Alt to dictate.
"""
import threading
import os
import logging
from PyQt6.QtCore import QObject, pyqtSignal

log = logging.getLogger("clawvoice")


class ClawVoice(QObject):
    transcription_ready = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.is_recording = False
        self._hotkey_held = False
        self._injecting = False  # guard against re-entrant hotkey during paste
        self._keyboard_hook = None
        self._recorder = None
        self._setup_recorder()
        self._setup_hotkey()

    def _setup_recorder(self):
        try:
            from recorder import AudioRecorder
            self._recorder = AudioRecorder()
        except Exception as e:
            self.error_occurred.emit(f"Audio init failed: {e}")

    def _setup_hotkey(self):
        try:
            import keyboard
            self._keyboard_hook = keyboard.hook(self._key_handler)
        except Exception as e:
            msg = str(e)
            if "admin" in msg.lower() or "permission" in msg.lower():
                self.error_occurred.emit("Needs Administrator — right-click ClawVoice → Run as Admin")
            else:
                self.error_occurred.emit(f"Hotkey setup failed: {msg}")

    def _key_handler(self, event):
        # Skip all keyboard events while we're injecting text (Ctrl+V simulation)
        if self._injecting:
            return

        try:
            import keyboard as kb
            ctrl = kb.is_pressed('ctrl')
            alt = kb.is_pressed('alt')

            if ctrl and alt and not self._hotkey_held:
                self._hotkey_held = True
                self._on_press()
            elif self._hotkey_held and not (ctrl and alt):
                self._hotkey_held = False
                self._on_release()
        except Exception:
            pass

    def _on_press(self):
        if not self.is_recording and self._recorder:
            self.is_recording = True
            log.info("Recording started...")
            self.status_changed.emit("recording")
            threading.Thread(target=self._record, daemon=True).start()

    def _on_release(self):
        if self.is_recording and self._recorder:
            self.is_recording = False
            self._recorder.recording = False
            log.info("Recording stopped, transcribing...")
            self.status_changed.emit("transcribing")

    def _record(self):
        try:
            self._recorder.start()
        except Exception as e:
            err = str(e)
            if "permission" in err.lower() or "access" in err.lower():
                self.error_occurred.emit("Microphone permission denied")
            elif "not available" in err.lower() or "no device" in err.lower():
                self.error_occurred.emit("No microphone found")
            else:
                self.error_occurred.emit(f"Mic error: {err}")
            self.is_recording = False
            self.status_changed.emit("error")
            return

        # Recording finished, now process
        threading.Thread(target=self._process, daemon=True).start()

    def _process(self):
        try:
            audio_path = self._recorder.stop()
            if not audio_path:
                self.status_changed.emit("idle")
                return

            log.info("Processing audio...")
            from transcriber import Transcriber
            transcriber = Transcriber(self.config)
            result, error = transcriber.transcribe(audio_path)

            try:
                os.remove(audio_path)
            except Exception:
                pass

            if result:
                # Set injection guard BEFORE emitting signal
                self._injecting = True
                try:
                    self.transcription_ready.emit(result)
                finally:
                    # Clear guard after a delay to let paste complete
                    threading.Timer(0.8, self._clear_inject_guard).start()
                self.status_changed.emit("idle")
            elif error:
                self.error_occurred.emit(error)
                self.status_changed.emit("error")
            else:
                self.status_changed.emit("idle")

        except Exception as e:
            self.error_occurred.emit(f"Processing error: {e}")
            self.status_changed.emit("error")

    def _clear_inject_guard(self):
        self._injecting = False

    def shutdown(self):
        try:
            import keyboard
            if self._keyboard_hook:
                keyboard.unhook(self._keyboard_hook)
        except Exception:
            pass
        if self._recorder:
            self._recorder.terminate()
