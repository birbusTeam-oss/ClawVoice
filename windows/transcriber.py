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

    def transcribe(self, audio_path: str) -> tuple[str | None, str | None]:
        """Returns (text, error_message). One of them will be None."""
        if not self.config.anthropic_key:
            return None, "No API key — open Settings to add one"

        try:
            file_size = os.path.getsize(audio_path)

            # Skip near-silence (< 1KB)
            if file_size < 1024:
                return None, None  # silence, not an error

            # Hard cap — refuse to send huge files
            if file_size > MAX_AUDIO_MB * 1024 * 1024:
                return None, f"Recording too long (>{MAX_AUDIO_MB}MB) — try shorter clips"

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
                return None, None  # silence, not an error
            return text, None

        except Exception as e:
            err = str(e)
            # Classify the error for a better user message
            if "authentication" in err.lower() or "invalid x-api-key" in err.lower() or "api_key" in err.lower():
                return None, "Invalid API key — update it in Settings"
            elif "rate_limit" in err.lower() or "rate limit" in err.lower():
                return None, "Rate limit hit — wait a moment and try again"
            elif "timeout" in err.lower() or "timed out" in err.lower():
                return None, "Transcription timed out — check your connection"
            elif "connection" in err.lower() or "network" in err.lower():
                return None, "Network error — check your internet connection"
            elif "overloaded" in err.lower():
                return None, "Claude is overloaded — try again in a moment"
            else:
                return None, f"Transcription error: {err[:60]}"
