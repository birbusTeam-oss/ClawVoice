"""
ClawVoice for Windows
Hold Right Alt → speak → release → text appears wherever you're typing.
"""
import threading
import os
from PyQt6.QtCore import QObject, pyqtSignal
from recorder import AudioRecorder
from transcriber import Transcriber
from injector import TextInjector

class ClawVoice(QObject):
    transcription_ready = pyqtSignal(str)
    status_changed = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.recorder = AudioRecorder()
        self.injector = TextInjector()
        self.is_recording = False
        self._setup_hotkey()

    def _setup_hotkey(self):
        import keyboard
        keyboard.on_press_key("right alt", self._on_press, suppress=True)
        keyboard.on_release_key("right alt", self._on_release, suppress=True)

    def _on_press(self, e):
        if not self.is_recording:
            self.is_recording = True
            self.status_changed.emit("recording")
            threading.Thread(target=self.recorder.start, daemon=True).start()

    def _on_release(self, e):
        if self.is_recording:
            self.is_recording = False
            self.status_changed.emit("transcribing")
            threading.Thread(target=self._process, daemon=True).start()

    def _process(self):
        audio_path = self.recorder.stop()
        if not audio_path:
            self.status_changed.emit("idle")
            return

        # Always create fresh transcriber so it picks up latest saved API key
        transcriber = Transcriber(self.config)
        result = transcriber.transcribe(audio_path)

        if result:
            self.transcription_ready.emit(result)
        else:
            self.status_changed.emit("error")

        self.status_changed.emit("idle")
        try:
            os.remove(audio_path)
        except:
            pass
