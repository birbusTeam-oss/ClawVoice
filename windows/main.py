"""
ClawVoice for Windows — Hold Ctrl+Alt to dictate.
Crash-resilient: stays running no matter what.
"""
import threading
import os
import logging
import time
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
        self._injecting = False
        self._processing = False  # prevent overlapping transcriptions
        self._keyboard_hook = None
        self._recorder = None
        self._setup_recorder()
        self._setup_hotkey()

    def _setup_recorder(self):
        try:
            from recorder import AudioRecorder
            self._recorder = AudioRecorder()
        except Exception as e:
            log.error(f"Audio init failed: {e}")

    def _setup_hotkey(self):
        try:
            import keyboard
            self._keyboard_hook = keyboard.hook(self._key_handler)
            log.info("Hotkey registered: Ctrl+Alt")
        except Exception as e:
            msg = str(e)
            if "admin" in msg.lower() or "permission" in msg.lower():
                log.error("Needs Administrator — right-click ClawVoice → Run as Admin")
            else:
                log.error(f"Hotkey setup failed: {msg}")

    def _key_handler(self, event):
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
        if not self.is_recording and not self._processing and self._recorder:
            self.is_recording = True
            self.status_changed.emit("recording")
            threading.Thread(target=self._record, daemon=True).start()

    def _on_release(self):
        if self.is_recording and self._recorder:
            self.is_recording = False
            self._recorder.recording = False
            self.status_changed.emit("transcribing")

    def _record(self):
        try:
            self._recorder.start()
        except Exception as e:
            err = str(e)
            log.error(f"Mic error: {err}")
            self.error_occurred.emit(f"Mic error: {err[:60]}")
            self.is_recording = False
            self._reset()
            return
        # Recording done, now transcribe
        threading.Thread(target=self._process, daemon=True).start()

    def _process(self):
        self._processing = True
        try:
            audio_path = self._recorder.stop()
            if not audio_path:
                log.info("No audio captured")
                self._reset()
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
                log.info(f"Transcribed: {len(result.split())} words")
                self._injecting = True
                try:
                    self.transcription_ready.emit(result)
                except Exception as e:
                    log.error(f"Emit failed: {e}")
                # Clear inject guard after delay
                threading.Timer(1.0, self._clear_inject_guard).start()
            elif error:
                log.error(error)
                self.error_occurred.emit(error)
            else:
                log.info("Silence detected")

        except Exception as e:
            log.error(f"Processing error: {e}")
            try:
                self.error_occurred.emit(f"Error: {str(e)[:60]}")
            except Exception:
                pass
        finally:
            self._reset()

    def _reset(self):
        """Re-arm for next recording."""
        self.is_recording = False
        self._processing = False
        self._hotkey_held = False
        try:
            self.status_changed.emit("idle")
        except Exception:
            pass

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
