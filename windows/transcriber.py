import base64
import os
from anthropic import Anthropic

MAX_AUDIO_MB = 20  # ~13 min at 16kHz mono — hard cap before base64 blows up API
_client_cache = {}

def _get_client(api_key: str) -> Anthropic:
    """Reuse client per key instead of creating on every call."""
    if api_key not in _client_cache:
        _client_cache[api_key] = Anthropic(api_key=api_key, timeout=30.0)
    return _client_cache[api_key]


class Transcriber:
    def __init__(self, config):
        self.config = config

    def transcribe(self, audio_path: str) -> str | None:
        if not self.config.anthropic_key:
            print("No API key configured")
            return None

        try:
            file_size = os.path.getsize(audio_path)

            # Skip near-silence (< 1KB)
            if file_size < 1024:
                print("Audio too short, skipping")
                return None

            # Hard cap — refuse to send huge files
            if file_size > MAX_AUDIO_MB * 1024 * 1024:
                print(f"Audio too large ({file_size/1024/1024:.1f}MB), skipping")
                return None

            with open(audio_path, 'rb') as f:
                audio_data = base64.standard_b64encode(f.read()).decode('utf-8')

            client = _get_client(self.config.anthropic_key)
            message = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Transcribe this audio accurately. Fix punctuation and grammar. Remove filler words (uh, um, like, you know). Return ONLY the transcribed text — no quotes, no labels, no explanation."
                        },
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "audio/wav",
                                "data": audio_data
                            }
                        }
                    ]
                }]
            )

            text = message.content[0].text.strip()
            if text.lower() in ('', '[silence]', '[no speech detected]', '[inaudible]', '[nothing]'):
                return None
            return text

        except Exception as e:
            print(f"Transcription error: {e}")
            return None
