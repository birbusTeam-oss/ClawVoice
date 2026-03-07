import pyaudio
import wave
import tempfile
import threading

class AudioRecorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.recording = False
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000  # 16kHz — optimal for Whisper

    def start(self):
        self.frames = []
        self.recording = True
        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        while self.recording:
            data = self.stream.read(self.CHUNK, exception_on_overflow=False)
            self.frames.append(data)

    def stop(self):
        self.recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        if not self.frames:
            return None

        # Save to temp WAV file
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        with wave.open(tmp.name, 'wb') as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(self.frames))
        return tmp.name
