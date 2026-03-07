# ClawVoice for Windows

Hold **Right Alt** → speak → release → text appears wherever you're typing.

## Setup
1. Install Python 3.11+
2. `pip install -r requirements.txt`
3. `python run.py`
4. Right-click tray icon → Settings → add your API keys

## API Keys needed
- **Anthropic** (Claude cleanup): get at console.anthropic.com
- **OpenAI** (Whisper transcription): get at platform.openai.com

Both have free tiers. Typical usage costs pennies per day.

## Build standalone .exe
`pyinstaller --onefile --windowed --name ClawVoice run.py`

## How it works
1. Hold Right Alt — mic starts recording
2. Release Right Alt — recording stops
3. Audio sent to Whisper API for transcription
4. Raw text cleaned up by Claude (fixes grammar, removes filler words)
5. Final text typed into whatever field you're in
