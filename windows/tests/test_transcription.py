"""
Transcription tests — verifies offline transcriber works correctly.
Generates test WAV files and checks output quality.
"""
import os
import sys
import wave
import struct
import math
import tempfile
import unittest

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_sine_wav(path: str, duration: float = 1.0, freq: float = 440.0, sample_rate: int = 16000):
    """Generate a sine wave WAV file (pure tone, no speech)."""
    n_samples = int(duration * sample_rate)
    samples = [int(16000 * math.sin(2 * math.pi * freq * t / sample_rate)) for t in range(n_samples)]
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack(f'<{len(samples)}h', *samples))


def generate_silence_wav(path: str, duration: float = 1.0, sample_rate: int = 16000):
    """Generate a silent WAV file."""
    n_samples = int(duration * sample_rate)
    samples = [0] * n_samples
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack(f'<{len(samples)}h', *samples))


class TestTranscriberBasics(unittest.TestCase):
    """Test transcriber initialization and edge cases."""

    def test_clean_text_capitalization(self):
        from transcriber import _clean_text
        self.assertEqual(_clean_text("hello world"), "Hello world.")

    def test_clean_text_already_punctuated(self):
        from transcriber import _clean_text
        result = _clean_text("Hello world.")
        self.assertEqual(result, "Hello world.")

    def test_clean_text_multi_sentence(self):
        from transcriber import _clean_text
        result = _clean_text("hello world. how are you")
        self.assertEqual(result, "Hello world. How are you.")

    def test_clean_text_empty(self):
        from transcriber import _clean_text
        self.assertEqual(_clean_text(""), "")
        self.assertEqual(_clean_text("  "), "")

    def test_clean_text_whitespace_normalization(self):
        from transcriber import _clean_text
        result = _clean_text("hello   world  ,  test")
        self.assertEqual(result, "Hello world, test.")

    def test_transcriber_init(self):
        from config import Config
        from transcriber import Transcriber
        config = Config()
        t = Transcriber(config)
        self.assertIsNotNone(t)

    def test_transcriber_missing_file(self):
        from config import Config
        from transcriber import Transcriber
        config = Config()
        t = Transcriber(config)
        result, error = t.transcribe("/nonexistent/path.wav")
        self.assertIsNone(result)
        self.assertIn("not found", error)

    def test_transcriber_tiny_file(self):
        """Files under 2KB should return None (too small for speech)."""
        from config import Config
        from transcriber import Transcriber
        config = Config()
        t = Transcriber(config)

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(b'\x00' * 100)
            path = f.name
        try:
            result, error = t.transcribe(path)
            self.assertIsNone(result)
        finally:
            os.unlink(path)

    def test_silence_produces_no_text(self):
        """A silent WAV should produce no transcription."""
        from config import Config
        from transcriber import Transcriber
        config = Config()
        t = Transcriber(config)

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            path = f.name
        generate_silence_wav(path, duration=2.0)
        try:
            result, error = t.transcribe(path)
            # Should be None (no speech) or an empty result
            # Error is acceptable if no backend available
            if result is not None:
                self.assertEqual(result.strip(), "")
        finally:
            os.unlink(path)


class TestVAD(unittest.TestCase):
    """Test VAD module."""

    def test_energy_vad_silence(self):
        from vad import has_speech_energy
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            path = f.name
        generate_silence_wav(path, duration=1.0)
        try:
            self.assertFalse(has_speech_energy(path, threshold=500))
        finally:
            os.unlink(path)

    def test_energy_vad_tone(self):
        from vad import has_speech_energy
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            path = f.name
        generate_sine_wav(path, duration=1.0, freq=440)
        try:
            self.assertTrue(has_speech_energy(path, threshold=500))
        finally:
            os.unlink(path)


class TestModelManager(unittest.TestCase):
    """Test model manager initialization."""

    def test_init(self):
        from config import Config
        from model_manager import ModelManager
        config = Config()
        mm = ModelManager(config)
        self.assertFalse(mm.is_loaded())
        self.assertEqual(mm.model_name, "base.en")


if __name__ == '__main__':
    unittest.main()
