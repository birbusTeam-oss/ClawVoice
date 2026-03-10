"""
ClawVoice for Windows — Hold Ctrl+Alt to dictate.
"""
import threading
import os
from PyQt6.QtCore import QObject, pyqtSignal
from recorder import AudioRecorder
from transcriber import Transcriber
from injector import inject


class ClawVoice(QObject):
    transcription_ready = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)   # emits a human-readable error message

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.recorder = AudioRecorder()
        self.is_recording = False
        self._hotkey_held = False
        self._keyboard_hook = None
        self._hotkey_registered = False
        self._setup_hotkey()

    def _setup_hotkey(self):
        try:
            import keyboard
            self._keyboard_hook = keyboard.hook(self._key_handler)
            self._hotkey_registered = True
        except ImportError:
            self.error_occurred.emit("keyboard library missing — reinstall ClawVoice")
            self.status_changed.emit("error")
        except Exception as e:
            msg = str(e)
            if "admin" in msg.lower() or "permission" in msg.lower() or "access" in msg.lower():
                self.error_occurred.emit("Hotkey needs Administrator — right-click → Run as Admin")
            elif "conflict" in msg.lower():
                self.error_occurred.emit("Ctrl+Alt hotkey conflict — try running as Admin")
            else:
                self.error_occurred.emit(f"Hotkey setup failed: {msg}")
            self.status_changed.emit("error")

    def _key_handler(self, event):
        import keyboard as kb
        ctrl = kb.is_pressed('ctrl')
        alt = kb.is_pressed('alt')
        # Both held -> start recording
        if ctrl and alt and not self._hotkey_held:
            self._hotkey_held = True
            self._on_press()
        # Either released while recording -> stop
        elif self._hotkey_held and not (ctrl and alt):
            self._hotkey_held = False
            self._on_release()

    def _on_press(self):
        if not self.is_recording:
            self.is_recording = True
            self.status_changed.emit("recording")
            threading.Thread(target=self._record, daemon=True).start()

    def _on_release(self):
        if self.is_recording:
            self.is_recording = False
            # CRITICAL: signal the recorder loop to stop
            self.recorder.recording = False
            self.status_changed.emit("transcribing")

    def _record(self):
        try:
            self.recorder.start()
        except RuntimeError as e:
            err = str(e)
            if "permission" in err.lower() or "access" in err.lower():
                self.error_occurred.emit("Microphone permission denied")
            elif "not available" in err.lower() or "no device" in err.lower():
                self.error_occurred.emit("No microphone found — check sound settings")
            else:
                self.error_occurred.emit(f"Mic error: {err}")
            self.is_recording = False
            self.status_changed.emit("error")
            return

        # start() returns when recording stops — now process
        threading.Thread(target=self._process, daemon=True).start()

    def _process(self):
        try:
            audio_path = self.recorder.stop()
            if not audio_path:
                self.status_changed.emit("idle")
                return

            transcriber = Transcriber(self.config)
            result, error = transcriber.transcribe(audio_path)

            if result:
                self.transcription_ready.emit(result)
                self.status_changed.emit("idle")
            elif error:
                self.error_occurred.emit(error)
                self.status_changed.emit("error")
            else:
                # Silence or empty — just idle, no error
                self.status_changed.emit("idle")

            try:
                os.remove(audio_path)
            except Exception:
                pass
        except Exception as e:
            self.error_occurred.emit(f"Processing error: {e}")
            self.status_changed.emit("error")

    def shutdown(self):
        """Clean shutdown — unhook keyboard, terminate audio."""
        try:
            import keyboard
            if self._keyboard_hook:
                keyboard.unhook(self._keyboard_hook)
        except Exception:
            pass
        self.recorder.terminate()
