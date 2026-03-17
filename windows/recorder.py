import pyaudio
import wave
import tempfile
import threading
import time

MAX_RECORD_SECONDS = 120  # 2 min cap -- prevents unbounded memory + huge API payloads

class AudioRecorder:
    def __init__(self):
        self._pa = None
        self.stream = None
        self.frames = []
        self.recording = False
        self._lock = threading.Lock()
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000

    def _get_pa(self):
        if self._pa is None:
            self._pa = pyaudio.PyAudio()
        return self._pa

    def start(self):
        with self._lock:
            if self.recording:
                return
            self.frames = []
            self.recording = True

        try:
            pa = self._get_pa()
            stream = pa.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            with self._lock:
                self.stream = stream

            start_time = time.time()
            while self.recording:
                # Auto-stop at max duration
                if time.time() - start_time > MAX_RECORD_SECONDS:
                    self.recording = False
                    break
                try:
                    data = stream.read(self.CHUNK, exception_on_overflow=False)
                    self.frames.append(data)
                except OSError:
                    break

        except OSError as e:
            print(f"Microphone error: {e}")
            self.recording = False
            raise RuntimeError(f"Microphone not available: {e}")
        finally:
            # Always clean up stream
            try:
                if self.stream:
                    self.stream.stop_stream()
                    self.stream.close()
            except Exception:
                pass
            with self._lock:
                self.stream = None

    def stop(self):
        self.recording = False
        # Give the read loop a moment to exit cleanly
        time.sleep(0.1)

        if not self.frames:
            return None

        try:
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            pa = self._get_pa()
            with wave.open(tmp.name, 'wb') as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(pa.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(b''.join(self.frames))
            return tmp.name
        except Exception as e:
            print(f"Failed to save audio: {e}")
            return None

    def terminate(self):
        """Call on app exit to release PortAudio resources."""
        if self._pa:
            try:
                self._pa.terminate()
            except Exception:
                pass
            self._pa = None
