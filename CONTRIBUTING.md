# Contributing to ClawVoice

Thanks for wanting to help. ClawVoice is built by a small team and we welcome contributions.

## Project structure

```
android/          ← Android app (Kotlin, min SDK 26)
windows/          ← Windows app (Python + PyQt6)
docs/             ← Architecture and documentation
.github/          ← GitHub Actions build workflows
```

## Getting started

```bash
git clone https://github.com/birbusTeam-oss/ClawVoice
```

**Android:** Open `android/` in Android Studio. Get an Anthropic API key from console.anthropic.com for testing — store it in the app settings, never hardcode it.

**Windows:** 
```bash
cd windows
pip install -r requirements.txt
python run.py
```

## Guidelines

- **No telemetry** — we collect zero data. Don't add any.
- **No new API dependencies** — ClawVoice uses Anthropic only. Keep it that way.
- **Privacy first** — audio goes: device → Anthropic API. Nothing else.
- **API keys** — never hardcode. Always use encrypted storage or user input.
- **Android:** Follow standard Kotlin conventions. Min SDK 26.
- **Windows:** Python 3.11+, PyQt6 for UI.

## Pull requests

- One feature or fix per PR
- Short description of what and why
- Test on a real device if possible

## Reporting bugs

Open an issue with:
- Platform (Windows / Android version)
- Steps to reproduce
- What you expected vs what happened

## Ideas for contribution

- [ ] macOS app (Swift + Accessibility API)
- [ ] Linux app (GTK + AT-SPI)
- [ ] Hotkey customization (Windows)
- [ ] Offline mode using local Whisper
- [ ] Custom Claude prompt styles (formal, casual, bullet points)
- [ ] Volume button trigger (Android)
- [ ] Auto-punctuation toggle

Open issues marked `good first issue` are a good starting point.
