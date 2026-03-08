# ClawVoice 🎙️

> Open source voice dictation for any app — powered by Claude AI.

**Hold a button. Speak. Text appears wherever you're typing.**

You deserve voice dictation that's open, free, and respects your privacy.
No subscription. No backend. No data collection. Just your API key and your voice.

---

## Download

| Platform | Download | Requirements |
|----------|----------|--------------|
| **Windows** | [⬇️ ClawVoice.exe](https://github.com/birbusTeam-oss/ClawVoice/releases/latest) | Windows 10/11 |
| **Android** | [⬇️ ClawVoice.apk](https://github.com/birbusTeam-oss/ClawVoice/releases/latest) | Android 8.0+ |

---

## How it works

```
You speak → Claude transcribes + cleans it up → text appears in any app
```

1. **Windows:** Hold `Right Alt` anywhere → speak → release → text is typed for you
2. **Android:** Tap the floating mic button → speak → tap again → text injected into any field

Works in Gmail, Chrome, Word, Slack, Notes, Messages — anything with a text field.

---

## Why ClawVoice?

Voice dictation should be open and free infrastructure.

Bring your own Anthropic API key — typical usage costs pennies per day. Your audio goes directly from your device to Anthropic's API. No middleman. One key. That's it.

---

## Setup

### API Key
Get your free Anthropic API key at [console.anthropic.com](https://console.anthropic.com)

That's the only key you need. ClawVoice uses Claude for everything.

### Windows
1. Download `ClawVoice.exe` from [releases](https://github.com/birbusTeam-oss/ClawVoice/releases/latest)
2. Double-click to run — no installation needed
3. Right-click the tray icon → **Settings**
4. Enter your Anthropic API key
5. Hold `Right Alt` anywhere to start dictating

### Android
1. Download `ClawVoice.apk` from [releases](https://github.com/birbusTeam-oss/ClawVoice/releases/latest)
2. Enable **Install unknown apps** in Android Settings → Security
3. Tap the APK to install
4. Open ClawVoice → enter your Anthropic API key
5. Grant **Accessibility** and **Overlay** permissions when prompted
6. Tap the floating mic button to dictate into any app

---

## Features

- 🎙️ **Works in any app** — Gmail, Chrome, Word, Slack, Notes, everything
- 🤖 **Claude-powered** — transcription and cleanup in one shot, no pipeline complexity
- 🔒 **Zero data collection** — audio goes directly to Anthropic's API
- 🖥️ **Windows** — system tray app, `Right Alt` hotkey, color-coded status
- 📱 **Android** — floating overlay button, works system-wide
- ⚡ **Hardware-encrypted key storage** — Android Keystore + AES256-GCM
- 🌍 **Multi-language** — speaks your language, Claude handles the rest
- 🆓 **Free and open source** — MIT license, forever

---

## Privacy

Your audio goes directly from your device to Anthropic's API.

We have **no servers**. We store **no data**. We see **nothing**.

The source code is public — verify it yourself.

---

## Building from source

```bash
git clone https://github.com/birbusTeam-oss/ClawVoice
```

**Windows:**
```bash
cd windows
pip install -r requirements.txt
python run.py
```

**Android:** Open the `android/` folder in Android Studio → Run.

See [android/BUILD.md](android/BUILD.md) for full build instructions.

---

## Contributing

PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

*Built by the Birbus Team — open source forever.*
