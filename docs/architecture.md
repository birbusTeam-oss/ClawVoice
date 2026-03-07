# ClawVoice Architecture

## Overview

ClawVoice is a privacy-first voice dictation app. No backend. No accounts. No subscriptions.

```
[User speaks]
     ↓
[VoiceRecordingService] ← foreground service, mic capture
     ↓ .m4a audio file
[ClaudeApiClient.transcribeAudio()]
     ↓ raw text (via Whisper or Claude)
[ClaudeApiClient.cleanupTranscription()] ← optional Claude pass
     ↓ clean text
[TextInjectionService.injectText()]
     ↓ AccessibilityService ACTION_SET_TEXT
[Focused input field in any app]
```

## Components

### VoiceRecordingService
- Android Foreground Service (type: microphone)
- Uses MediaRecorder to capture M4A audio
- Handles START/STOP intents
- Coordinates the transcription pipeline
- Shows notification during recording

### ClaudeApiClient
- Sends audio to transcription service (Whisper API or future Claude audio)
- Optionally passes raw text to Claude for grammar/punctuation cleanup
- User provides their own Anthropic API key — stored in SharedPreferences
- Zero backend — all calls go directly to Anthropic

### TextInjectionService
- Android AccessibilityService
- Traverses the active window node tree to find focused editable fields
- Uses ACTION_SET_TEXT to inject transcribed text
- Works across ALL apps — no app-specific integrations needed

### MainActivity
- Settings UI: API key entry, accessibility service toggle
- Floating overlay button (planned)
- Recording status display

## Transcription Strategy

**Current:** Placeholder (returns dummy text)

**Phase 1:** Whisper API (OpenAI) for speech-to-text

**Phase 2:** Claude for cleanup pass

**Phase 3 (future):** Claude native audio

**Phase 4 (future):** Local Whisper (offline)

## Privacy Model

- Audio recorded locally to app cache
- Sent directly to Anthropic API (or OpenAI for Whisper)
- Deleted after transcription
- No server, no logging, no account
- API key stored in Android SharedPreferences (encrypted)

## Permissions Required

| Permission | Why |
|-----------|-----|
| RECORD_AUDIO | Capture microphone |
| INTERNET | Call Anthropic/OpenAI APIs |
| SYSTEM_ALERT_WINDOW | Floating overlay button |
| FOREGROUND_SERVICE | Keep recording service alive |
| BIND_ACCESSIBILITY_SERVICE | Inject text into any app |
