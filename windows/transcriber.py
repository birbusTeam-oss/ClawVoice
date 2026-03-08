import base64
import os
from anthropic import Anthropic

class Transcriber:
    def __init__(self, config):
        self.config = config

    def transcribe(self, audio_path: str) -> str | None:
        """
        Send audio directly to Claude for transcription + cleanup.
        One API, one key, one step.
        """
        if not self.config.anthropic_key:
            return None

        try:
            # Read and encode audio file
            with open(audio_path, 'rb') as f:
                audio_data = base64.standard_b64encode(f.read()).decode('utf-8')

            client = Anthropic(api_key=self.config.anthropic_key)

            message = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Transcribe this audio accurately. Fix punctuation and grammar. Remove filler words like uh, um, like. Return ONLY the transcribed text, nothing else."
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

            return message.content[0].text.strip()

        except Exception as e:
            print(f"Transcription error: {e}")
            return None
