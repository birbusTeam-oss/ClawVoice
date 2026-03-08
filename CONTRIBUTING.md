# Contributing to ClawVoice

Thanks for wanting to help. ClawVoice is built by a small team and we welcome contributions.

> **End user?** Just download the `.exe` or `.apk` from [releases](https://github.com/birbusTeam-oss/ClawVoice/releases/latest) — no setup needed.

## Project structure

```
android/          ← Android app (Kotlin, min SDK 26)
windows/          ← Windows app (Python + PyQt6, built to .exe via PyInstaller)
docs/             ← Architecture and documentation
.github/          ← GitHub Actions CI/CD (builds exe + apk automatically)
```

## Getting started (developers)

```bash
git clone https://github.com/birbusTeam-oss/ClawVoice
```

**Android:** Open `android/` in Android Studio. Get an Anthropic API key from [console.anthropic.com](https://console.anthropic.com) for testing — store it in app settings, never hardcode it.

**Windows (run from source):**
```bash
cd windows
pip install -r requirements.txt
python run.py
```

**Windows (build your own .exe):**
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name ClawVoice --icon=assets/icon.ico run.py
# Output: dist/ClawVoice.exe
```

## Guidelines

- **No telemetry** — we collect zero data. Don't add any.
- **Anthropic only** — ClawVoice uses one API. Keep it that way.
- **Privacy first** — audio goes: device → Anthropic API. Nothing else.
- **API keys** — never hardcode. Always use encrypted storage or user input.
- **Android:** Standard Kotlin conventions. Min SDK 26.
- **Windows:** Python 3.11+, PyQt6 for UI.

## Pull requests

- One feature or fix per PR
- Short description of what and why
- Test on a real device if possible

## Reporting bugs

Open an issue with:
- Platform (Windows 10/11 or Android version)
- Steps to reproduce
- What you expected vs what happened

## Roadmap / ideas

- [ ] macOS app (Swift + Accessibility API)
- [ ] Linux app (GTK + AT-SPI)
- [ ] Hotkey customization (Windows)
- [ ] Offline mode (local Whisper)
- [ ] Custom Claude prompt styles (formal, casual, bullet points)
- [ ] Volume button trigger (Android)
- [ ] Auto-punctuation toggle

Open issues marked `good first issue` are a good place to start.
