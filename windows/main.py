"""
ClawVoice for Windows
Hold Ctrl+Space → speak → release → text appears wherever you're typing.
"""
import threading
import os
import sys
from PyQt6.QtCore import QObject, pyqtSignal
from recorder import AudioRecorder
from transcriber import Transcriber
from injector import inject


class ClawVoice(QObject):
    transcription_ready = pyqtSignal(str)
    status_changed = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.recorder = AudioRecorder()
        self.is_recording = False
        self._hotkey_held = False
        self._setup_hotkey()

    def _setup_hotkey(self):
        try:
            import keyboard
            keyboard.hook(self._key_handler)
        except Exception as e:
            print(f"Hotkey setup failed (need admin?): {e}")
            self.status_changed.emit("error")

    def _key_handler(self, event):
        import keyboard as kb
        # Ctrl+Space = hold to talk
        if event.name == 'space' and kb.is_pressed('ctrl'):
            if event.event_type == 'down' and not self._hotkey_held:
                self._hotkey_held = True
                self._on_press()
            elif event.event_type == 'up' and self._hotkey_held:
                self._hotkey_held = False
                self._on_release()

    def _on_press(self):
        if not self.is_recording:
            self.is_recording = True
            self.status_changed.emit("recording")
            threading.Thread(target=self.recorder.start, daemon=True).start()

    def _on_release(self):
        if self.is_recording:
            self.is_recording = False
            self.status_changed.emit("transcribing")
            threading.Thread(target=self._process, daemon=True).start()

    def _process(self):
        try:
            audio_path = self.recorder.stop()
            if not audio_path:
                self.status_changed.emit("idle")
                return

            transcriber = Transcriber(self.config)
            result = transcriber.transcribe(audio_path)

            if result:
                self.transcription_ready.emit(result)
                self.status_changed.emit("idle")
            else:
                self.status_changed.emit("error")

            try:
                os.remove(audio_path)
            except:
                pass
        except Exception as e:
            print(f"Processing error: {e}")
            self.status_changed.emit("error")
