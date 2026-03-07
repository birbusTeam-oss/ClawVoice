import os
import requests
import json
from anthropic import Anthropic

class Transcriber:
    def __init__(self, config):
        self.config = config

    def transcribe(self, audio_path: str) -> str | None:
        """
        Step 1: Transcribe audio using OpenAI Whisper API
        Step 2: Clean up with Claude (optional, if Anthropic key set)
        """
        raw_text = self._whisper_transcribe(audio_path)
        if not raw_text:
            return None

        # Claude cleanup pass — fixes grammar, punctuation, formatting
        if self.config.anthropic_key:
            return self._claude_cleanup(raw_text)
        return raw_text

    def _whisper_transcribe(self, audio_path: str) -> str | None:
        if not self.config.openai_key:
            return None
        try:
            with open(audio_path, 'rb') as f:
                response = requests.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {self.config.openai_key}"},
                    files={"file": ("audio.wav", f, "audio/wav")},
                    data={"model": "whisper-1", "language": "en"}
                )
            return response.json().get("text", "").strip()
        except Exception as e:
            print(f"Whisper error: {e}")
            return None

    def _claude_cleanup(self, raw_text: str) -> str:
        try:
            client = Anthropic(api_key=self.config.anthropic_key)
            message = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": f"Clean up this voice transcription. Fix punctuation and grammar. Remove filler words (uh, um, like). Return ONLY the cleaned text:\n\n{raw_text}"
                }]
            )
            return message.content[0].text.strip()
        except Exception as e:
            print(f"Claude error: {e}")
            return raw_text  # Fall back to raw Whisper output
