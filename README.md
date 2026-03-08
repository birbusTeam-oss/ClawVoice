# ClawVoice 🎙️

> Open source voice dictation for any app — powered by Claude AI.

**Hold a button. Speak. Text appears wherever you're typing.**

You deserve voice dictation that's open, free, and respects your privacy.
No subscription. No backend. No data collection. Just your API key and your voice.

---

## Download

| Platform | File | Requirements |
|----------|------|--------------|
| **Windows** | [⬇️ ClawVoice.exe](https://github.com/birbusTeam-oss/ClawVoice/releases/latest) | Windows 10/11 — no install needed |
| **Android** | [⬇️ ClawVoice.apk](https://github.com/birbusTeam-oss/ClawVoice/releases/latest) | Android 8.0+ |

---

## How it works

```
You speak → Claude transcribes + cleans it up → text appears in any app
```

- **Windows:** Hold `Right Alt` anywhere → speak → release → text is typed for you
- **Android:** Tap the floating mic button → speak → tap again → text injected into any field

Works in Gmail, Chrome, Word, Slack, Notes, Messages — anything with a text field.

---

## Setup

### Step 1 — Get your API key
Get a free Anthropic API key at [console.anthropic.com](https://console.anthropic.com)

That's the only key you need. ClawVoice uses Claude for everything — transcription and cleanup in one step.

---

### Windows

1. Download [ClawVoice.exe](https://github.com/birbusTeam-oss/ClawVoice/releases/latest)
2. Double-click `ClawVoice.exe` — no installation, no Python required
3. Windows may show a security prompt — click **More info → Run anyway**
4. ClawVoice appears in your system tray (bottom right)
5. Right-click the tray icon → **Settings**
6. Paste your Anthropic API key → Save
7. Hold **Right Alt** anywhere to dictate

> 🟣 Tray icon is **purple** when idle · **red** while recording · **yellow** while transcribing

---

### Android

1. Download [ClawVoice.apk](https://github.com/birbusTeam-oss/ClawVoice/releases/latest)
2. On your phone: **Settings → Security → Install unknown apps** → enable for your browser/files app
3. Tap the APK file to install
4. Open ClawVoice → paste your Anthropic API key → Save
5. Tap **Grant** next to each permission:
   - **Overlay** — lets the floating mic button appear on screen
   - **Accessibility** — lets ClawVoice type into any app
6. Tap **Start ClawVoice**
7. Tap the floating 🎙️ button to start dictating — tap again to stop

---

## Features

- 🎙️ **Works in any app** — Gmail, Chrome, Word, Slack, Notes, everything
- 🤖 **Claude-powered** — transcription and cleanup in one call
- 🔒 **Zero data collection** — audio goes directly to Anthropic's API, nowhere else
- 🖥️ **Windows** — standalone `.exe`, system tray, Right Alt hotkey
- 📱 **Android** — floating mic overlay, works system-wide
- ⚡ **Encrypted key storage** — Android Keystore AES256-GCM, Windows AppData
- 🌍 **Multi-language** — speak any language, Claude handles the rest
- 🆓 **Free and open source** — MIT license, forever

---

## Privacy

Your audio goes directly from your device to Anthropic's API.

We have **no servers**. We store **no data**. We see **nothing**.

The source code is public — verify it yourself.

---

## Building from source

For developers who want to build from source or contribute:

```bash
git clone https://github.com/birbusTeam-oss/ClawVoice
```

**Windows:**
```bash
cd windows
pip install -r requirements.txt
python run.py

# To build your own .exe:
pip install pyinstaller
pyinstaller --onefile --windowed --name ClawVoice run.py
```

**Android:** Open the `android/` folder in Android Studio → Run.
Full build guide: [android/BUILD.md](android/BUILD.md)

---

## Contributing

PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

*Built by the Birbus Team — open source forever.*
