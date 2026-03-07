"""
ClawVoice for Windows
Open source voice dictation powered by Claude AI.
Hold Right Alt → speak → release → text appears wherever you're typing.
"""

import sys
import threading
import tempfile
import os
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from PyQt6.QtGui import QIcon
from recorder import AudioRecorder
from transcriber import Transcriber
from injector import TextInjector
from settings import SettingsWindow
from config import Config

class ClawVoice(QObject):
    transcription_ready = pyqtSignal(str)
    status_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.config = Config()
        self.recorder = AudioRecorder()
        self.transcriber = Transcriber(self.config)
        self.injector = TextInjector()
        self.is_recording = False
        self.setup_hotkey()

    def setup_hotkey(self):
        import keyboard
        keyboard.on_press_key("right alt", self.on_hotkey_press, suppress=True)
        keyboard.on_release_key("right alt", self.on_hotkey_release, suppress=True)

    def on_hotkey_press(self, e):
        if not self.is_recording:
            self.is_recording = True
            self.status_changed.emit("recording")
            threading.Thread(target=self.recorder.start, daemon=True).start()

    def on_hotkey_release(self, e):
        if self.is_recording:
            self.is_recording = False
            self.status_changed.emit("transcribing")
            threading.Thread(target=self.process_recording, daemon=True).start()

    def process_recording(self):
        audio_path = self.recorder.stop()
        if not audio_path:
            self.status_changed.emit("idle")
            return
        result = self.transcriber.transcribe(audio_path)
        if result:
            self.transcription_ready.emit(result)
        self.status_changed.emit("idle")
        try:
            os.remove(audio_path)
        except:
            pass
