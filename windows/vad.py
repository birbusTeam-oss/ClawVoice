"""
VAD (Voice Activity Detection) using silero-vad.
Trims silence from recordings and detects if speech is present.
"""
import logging
import wave
import struct
import os

log = logging.getLogger("clawvoice")

_vad_model = None


def _get_vad_model():
    """Load silero VAD model (cached)."""
    global _vad_model
    if _vad_model is None:
        try:
            import torch
            model, utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=True
            )
            _vad_model = (model, utils)
            log.info("Silero VAD loaded")
        except ImportError:
            log.warning("silero-vad requires torch. Falling back to energy-based VAD.")
            _vad_model = None
        except Exception as e:
            log.warning(f"VAD load failed: {e}. Using energy-based fallback.")
            _vad_model = None
    return _vad_model


def has_speech_energy(audio_path: str, threshold: float = 500.0) -> bool:
    """Simple energy-based speech detection fallback."""
    try:
        with wave.open(audio_path, 'rb') as wf:
            frames = wf.readframes(wf.getnframes())
            if len(frames) < 100:
                return False
            samples = struct.unpack(f'<{len(frames)//2}h', frames)
            rms = (sum(s*s for s in samples) / len(samples)) ** 0.5
            return rms > threshold
    except Exception as e:
        log.warning(f"Energy VAD failed: {e}")
        return True  # assume speech on error


def has_speech(audio_path: str, min_speech_duration: float = 0.3) -> bool:
    """
    Check if audio file contains speech.
    Uses silero-vad if available, falls back to energy-based detection.
    """
    vad = _get_vad_model()
    if vad is None:
        return has_speech_energy(audio_path)

    try:
        model, utils = vad
        (get_speech_timestamps, _, read_audio, _, _) = utils
        wav = read_audio(audio_path, sampling_rate=16000)
        timestamps = get_speech_timestamps(wav, model, sampling_rate=16000)

        total_speech = sum(
            (ts['end'] - ts['start']) / 16000.0
            for ts in timestamps
        )
        has = total_speech >= min_speech_duration
        log.info(f"VAD: {total_speech:.1f}s speech detected ({'pass' if has else 'skip'})")
        return has
    except Exception as e:
        log.warning(f"Silero VAD failed: {e}")
        return has_speech_energy(audio_path)


def trim_silence(audio_path: str, output_path: str = None) -> str:
    """
    Trim leading/trailing silence from audio.
    Returns path to trimmed audio (may be same file if no trimming needed).
    """
    vad = _get_vad_model()
    if vad is None:
        return audio_path  # no trimming without VAD

    try:
        import torch
        model, utils = vad
        (get_speech_timestamps, _, read_audio, _, collect_chunks) = utils

        wav = read_audio(audio_path, sampling_rate=16000)
        timestamps = get_speech_timestamps(wav, model, sampling_rate=16000)

        if not timestamps:
            return audio_path

        # Add padding around speech segments
        padding = int(0.2 * 16000)  # 200ms padding
        first_start = max(0, timestamps[0]['start'] - padding)
        last_end = min(len(wav), timestamps[-1]['end'] + padding)

        trimmed = wav[first_start:last_end]

        if output_path is None:
            output_path = audio_path.replace('.wav', '_trimmed.wav')

        # Write trimmed audio
        import torchaudio
        torchaudio.save(output_path, trimmed.unsqueeze(0), 16000)
        log.info(f"Trimmed: {len(wav)/16000:.1f}s -> {len(trimmed)/16000:.1f}s")
        return output_path

    except Exception as e:
        log.warning(f"Trim failed: {e}")
        return audio_path
