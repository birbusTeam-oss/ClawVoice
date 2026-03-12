"""
ClawVoice for Windows — Hold Ctrl+Alt to dictate.
Uses pynput for BOTH hotkey detection and text injection.
No keyboard library = no hook conflicts = no crashes.
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
        self._processing = False
        self._injecting = False
        self._ctrl_held = False
        self._alt_held = False
        self._recorder = None
        self._transcriber = None
        self._listener = None
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
            from pynput.keyboard import Listener, Key
            self._Key = Key
            self._listener = Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self._listener.daemon = True
            self._listener.start()
            log.info("Hotkey registered: Ctrl+Alt")
        except Exception as e:
            log.error(f"Hotkey setup failed: {e}")

    def _on_key_press(self, key):
        if self._injecting or self._processing:
            return
        try:
            Key = self._Key
            if key == Key.ctrl_l or key == Key.ctrl_r:
                self._ctrl_held = True
            elif key == Key.alt_l or key == Key.alt_r or key == Key.alt_gr:
                self._alt_held = True

            if self._ctrl_held and self._alt_held and not self.is_recording and not self._processing:
                self.is_recording = True
                self.status_changed.emit("recording")
                threading.Thread(target=self._record, daemon=True).start()
        except Exception:
            pass

    def _on_key_release(self, key):
        try:
            Key = self._Key
            released_ctrl = (key == Key.ctrl_l or key == Key.ctrl_r)
            released_alt = (key == Key.alt_l or key == Key.alt_r or key == Key.alt_gr)

            if released_ctrl:
                self._ctrl_held = False
            if released_alt:
                self._alt_held = False

            # If either key released while recording, stop
            if self.is_recording and (released_ctrl or released_alt):
                self.is_recording = False
                if self._recorder:
                    self._recorder.recording = False
                self.status_changed.emit("transcribing")
        except Exception:
            pass

    def _record(self):
        try:
            self._recorder.start()
        except Exception as e:
            log.error(f"Mic error: {e}")
            self.error_occurred.emit(f"Mic error: {str(e)[:60]}")
            self._reset()
            return
        threading.Thread(target=self._process, daemon=True).start()

    def _get_transcriber(self):
        if self._transcriber is None:
            from transcriber import Transcriber
            self._transcriber = Transcriber(self.config)
        return self._transcriber

    def _process(self):
        self._processing = True
        try:
            audio_path = self._recorder.stop()
            if not audio_path:
                log.info("No audio captured")
                self._reset()
                return

            log.info("Processing audio...")
            transcriber = self._get_transcriber()
            result, error = transcriber.transcribe(audio_path)

            # Auto-retry once on non-API errors
            if error and "API" not in error and "internet" not in error:
                log.info("Retrying...")
                time.sleep(0.3)
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
        self.is_recording = False
        self._processing = False
        self._ctrl_held = False
        self._alt_held = False
        try:
            self.status_changed.emit("idle")
        except Exception:
            pass

    def _clear_inject_guard(self):
        self._injecting = False

    def shutdown(self):
        if self._listener:
            try:
                self._listener.stop()
            except Exception:
                pass
        if self._recorder:
            self._recorder.terminate()
