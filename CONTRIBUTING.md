# Contributing to ClawVoice

Thanks for wanting to help! ClawVoice is built for developers by developers.

## Getting Started

1. Fork the repo
2. Clone your fork
3. Open `android/` in Android Studio
4. Create a `local.properties` with your API key for testing (never commit this)

## Project Structure

```
android/          ← Android app (Kotlin)
windows/          ← Windows app (coming soon)
docs/             ← Architecture docs
```

## Guidelines

- **Android:** Follow standard Kotlin conventions. Min SDK 26.
- **No telemetry:** We don't collect data. Don't add any.
- **API keys:** Never hardcode. Always use SharedPreferences or user input.
- **Privacy first:** Audio goes user → Anthropic API. That's it.

## Pull Requests

- One feature/fix per PR
- Add a short description of what and why
- Test on a real device if possible (emulator for basic stuff is fine)

## Issues

Found a bug? Open an issue with:
- Android version
- Steps to reproduce
- What you expected vs what happened

## Roadmap Ideas

- [ ] Real Whisper API integration (transcription)
- [ ] Floating overlay button
- [ ] Volume button trigger
- [ ] Windows app (WinRT + accessibility)
- [ ] Custom Claude prompts for formatting style
- [ ] Offline mode (local Whisper)

Jump in on any open issue marked `good first issue`.
