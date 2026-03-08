# ClawVoice Architecture

## Overview

ClawVoice is a privacy-first voice dictation tool. No backend. No accounts. No subscriptions.

```
[User speaks]
      ↓
[Recording layer]        ← mic capture (WAV/M4A)
      ↓ audio file
[Claude API]             ← base64 audio → transcription + cleanup in one call
      ↓ clean text
[Text injection layer]   ← types result into focused field in any app
      ↓
[Wherever you're typing]
```

One API. One key. One company.

---

## Android components

### VoiceRecordingService
- Android Foreground Service (type: microphone)
- Captures audio at 16kHz WAV via MediaRecorder
- Handles START/STOP intents from the floating overlay button
- Coordinates the full transcription pipeline
- Shows persistent notification during recording

### ClaudeApiClient
- Encodes audio as base64
- Sends directly to `api.anthropic.com/v1/messages` with Claude Haiku
- Claude transcribes AND cleans up in one call — no separate cleanup pass needed
- Certificate pinned to `api.anthropic.com` (rejects MITM attacks)
- API key stored in Android Keystore via EncryptedSharedPreferences (AES256-GCM)

### TextInjectionService
- Android AccessibilityService
- Walks the active window node tree to find the focused editable field
- Injects transcribed text via `ACTION_SET_TEXT`
- Works in ALL apps — no app-specific integrations

### SecureStorage
- Wraps Android Keystore with AES256-GCM encryption
- API key never stored in plaintext anywhere on the device
- Even with physical device access, key cannot be extracted without the user's PIN/biometrics

### MainActivity
- Settings UI: API key input, permission status, how-to guide
- Dark theme, modern card layout

---

## Windows components

### VoiceRecordingService (recorder.py)
- Captures microphone input at 16kHz via PyAudio
- Saves to temporary WAV file
- Start/stop controlled by global hotkey (Right Alt)

### Transcriber (transcriber.py)
- Encodes WAV as base64
- Sends to Claude API — transcription and cleanup in one call
- Falls back gracefully if API call fails

### TextInjector (injector.py)
- Clipboard-based injection: copies text → simulates Ctrl+V in focused field
- Works in any Windows app

### Config (config.py)
- Stores API key in `%APPDATA%\ClawVoice\config.json`
- Settings window (settings.py): dark PyQt6 UI, frameless window

### TrayManager (tray.py)
- System tray icon with color status:
  - 🟣 Purple = idle, ready
  - 🔴 Red = recording
  - 🟡 Yellow = transcribing
- Right-click menu: Settings, Quit

---

## Privacy model

| Step | Where it goes |
|------|--------------|
| Audio captured | Stays on device (temp file) |
| Sent to | `api.anthropic.com` only (cert pinned) |
| Deleted after | Immediately after transcription |
| API key | Encrypted on device, never transmitted |
| Usage data | Not collected. Ever. |

---

## Permissions

### Android
| Permission | Why |
|-----------|-----|
| RECORD_AUDIO | Capture microphone |
| INTERNET | Call Anthropic API |
| SYSTEM_ALERT_WINDOW | Floating mic overlay button |
| FOREGROUND_SERVICE | Keep recording service alive in background |
| BIND_ACCESSIBILITY_SERVICE | Inject text into any app |
| QUERY_ALL_PACKAGES | List installed apps for future features |

### Windows
- Microphone access (requested at runtime)
- No admin rights required
