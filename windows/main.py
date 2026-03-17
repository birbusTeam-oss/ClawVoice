"""
ClawVoice -- Hold Ctrl+Alt to dictate.
Flag-based: pynput sets flags, QTimer processes on main thread.
"""
import threading
import os
import logging
import time
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

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
        self._want_start = False
        self._want_stop = False
        self._cooldown_until = 0  # timestamp -- no new recording until this time
        self._recorder = None
        self._transcriber = None
        self._model_manager = None
        self._listener = None
        self._poll_timer = None
        self._setup_recorder()
        self._setup_model_manager()

    def _setup_recorder(self):
        try:
            from recorder import AudioRecorder
            self._recorder = AudioRecorder()
            log.info("Recorder initialized")
        except Exception as e:
            log.error(f"Audio init failed: {e}")

    def _setup_model_manager(self):
        try:
            from model_manager import ModelManager
            self._model_manager = ModelManager(self.config)
            # Load model in background to avoid blocking startup
            threading.Thread(target=self._model_manager.load, daemon=True).start()
            log.info("Model manager initialized (loading in background)")
        except ImportError:
            log.warning("faster-whisper not installed, will use cloud transcription")
            self._model_manager = None
        except Exception as e:
            log.error(f"Model manager init failed: {e}")
            self._model_manager = None

    def start_listening(self):
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
            return

        self._poll_timer = QTimer()
        self._poll_timer.timeout.connect(self._poll_flags)
        self._poll_timer.start(50)
        log.info("Poll timer started")

    def _on_key_press(self, key):
        """pynput callback -- ONLY sets flags."""
        if self._injecting or self._processing:
            return
        try:
            Key = self._Key
            if key == Key.ctrl_l or key == Key.ctrl_r:
                self._ctrl_held = True
            elif key == Key.alt_l or key == Key.alt_r or key == Key.alt_gr:
                self._alt_held = True

            if self._ctrl_held and self._alt_held and not self.is_recording:
                self._want_start = True
        except Exception:
            pass

    def _on_key_release(self, key):
        """pynput callback -- ONLY sets flags."""
        try:
            Key = self._Key
            if key == Key.ctrl_l or key == Key.ctrl_r:
                self._ctrl_held = False
                if self.is_recording:
                    self._want_stop = True
            elif key == Key.alt_l or key == Key.alt_r or key == Key.alt_gr:
                self._alt_held = False
                if self.is_recording:
                    self._want_stop = True
        except Exception:
            pass

    def _poll_flags(self):
        """Main thread -- processes flags from pynput."""
        now = time.time()

        # Stop takes priority over start
        if self._want_stop and self.is_recording:
            self._want_stop = False
            self._want_start = False  # discard any stale start
            self._stop_recording()
            return

        if self._want_start and not self.is_recording and not self._processing:
            if now < self._cooldown_until:
                self._want_start = False  # too soon, discard
                return
            self._want_start = False
            self._start_recording()

    def _start_recording(self):
        if not self._recorder:
            return
        self.is_recording = True
        self._processing = True  # block new recordings until transcription done
        self._want_start = False
        self._want_stop = False
        log.info("Recording started")
        self.status_changed.emit("recording")
        threading.Thread(target=self._record, daemon=True).start()

    def _stop_recording(self):
        self.is_recording = False
        self._want_stop = False
        self._want_start = False
        self._cooldown_until = time.time() + 1.5
        log.info("Recording stopping (0.5s tail buffer)...")
        self.status_changed.emit("transcribing")
        # Keep mic open 0.5s after key release to catch trailing words
        threading.Timer(0.5, self._finalize_stop).start()

    def _finalize_stop(self):
        if self._recorder:
            self._recorder.recording = False
        log.info("Recording stopped")

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
            self._transcriber = Transcriber(self.config, model_manager=self._model_manager)
        return self._transcriber

    def _process(self):
        try:
            audio_path = self._recorder.stop()
            if not audio_path:
                log.info("No audio captured")
                self._reset()
                return

            file_size = os.path.getsize(audio_path) if os.path.exists(audio_path) else 0
            log.info(f"Audio: {file_size // 1024}KB")

            # Skip tiny recordings (< 5KB = no real speech)
            if file_size < 5000:
                log.info("Recording too short, skipping")
                try:
                    os.remove(audio_path)
                except Exception:
                    pass
                self._reset()
                return

            log.info("Transcribing...")
            transcriber = self._get_transcriber()
            result, error = transcriber.transcribe(audio_path)

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
                self.transcription_ready.emit(result)
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
        self._want_start = False
        self._want_stop = False
        self._cooldown_until = time.time() + 0.5  # brief cooldown after reset
        try:
            self.status_changed.emit("idle")
        except Exception:
            pass

    def _clear_inject_guard(self):
        self._injecting = False

    def shutdown(self):
        if self._poll_timer:
            self._poll_timer.stop()
        if self._listener:
            try:
                self._listener.stop()
            except Exception:
                pass
        if self._recorder:
            self._recorder.terminate()
