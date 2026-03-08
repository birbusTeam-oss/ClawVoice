import base64
import os
from anthropic import Anthropic


class Transcriber:
    def __init__(self, config):
        self.config = config

    def transcribe(self, audio_path: str) -> str | None:
        """Send audio to Claude for transcription. One API call, one step."""
        if not self.config.anthropic_key:
            print("No API key configured")
            return None

        try:
            with open(audio_path, 'rb') as f:
                audio_data = base64.standard_b64encode(f.read()).decode('utf-8')

            # Skip tiny files (< 1KB = probably silence/noise)
            if os.path.getsize(audio_path) < 1024:
                print("Audio too short, skipping")
                return None

            client = Anthropic(
                api_key=self.config.anthropic_key,
                timeout=30.0,
            )

            message = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Transcribe this audio accurately. Fix punctuation and grammar. Remove filler words (uh, um, like, you know). Return ONLY the transcribed text, nothing else — no quotes, no labels, no explanation."
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
            # Filter out meta-responses from the model
            if text.lower() in ['', '[silence]', '[no speech detected]', '[inaudible]']:
                return None
            return text

        except Exception as e:
            print(f"Transcription error: {e}")
            return None
