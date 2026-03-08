# ClawVoice 🎙️

> Open source voice dictation for any app — powered by Claude AI.

**Hold Ctrl+Space. Speak. Text appears wherever you're typing.**

No subscription. No backend. No data collection. Just your API key and your voice.

---

## Download

| Platform | File | Requirements |
|----------|------|--------------|
| **Windows** | [⬇️ ClawVoice.exe](https://github.com/birbusTeam-oss/ClawVoice/releases/latest) | Windows 10/11 — no install needed |

> macOS support coming soon.

---

## How it works

```
Hold Ctrl+Space → speak → release → text appears in any app
```

A floating indicator appears while you're recording so you always know it's listening. Works in Gmail, Chrome, Word, Slack, Notion, anything with a text field.

---

## Setup

### Step 1 — Get your API key
Get a free Anthropic API key at [console.anthropic.com](https://console.anthropic.com)

That's the only key you need. ClawVoice uses Claude for everything.

---

### Windows

1. Download [ClawVoice.exe](https://github.com/birbusTeam-oss/ClawVoice/releases/latest)
2. Double-click `ClawVoice.exe` — no installation, no Python required
3. Windows may show a security prompt — click **More info → Run anyway**
4. ClawVoice appears in your system tray (bottom right)
5. Right-click the tray icon → **Settings**
6. Paste your Anthropic API key → **Save**
7. Hold **Ctrl+Space** anywhere to dictate — a floating bar appears while recording
8. Release **Ctrl+Space** to stop — text is typed automatically

> 🟣 Tray icon: **purple** = idle · **red** = recording · **yellow** = transcribing

---

## Features

- 🎙️ **Works in any app** — Gmail, Chrome, Word, Slack, Notion, everything
- 🤖 **Claude-powered** — transcription and cleanup in one call, no pipeline
- 🪟 **Floating indicator** — always know when it's listening
- ⌨️ **Ctrl+Space hotkey** — hold to talk, release to transcribe
- 🔒 **Zero data collection** — audio goes directly to Anthropic's API
- 🆓 **Free and open source** — MIT license, forever

---

## Privacy

Your audio goes directly from your device to Anthropic's API. We have no servers. We store no data. Ever. Source code is public — verify it yourself.

---

## Building from source

```bash
git clone https://github.com/birbusTeam-oss/ClawVoice
cd windows
pip install -r requirements.txt
python run.py

# Build your own .exe
pip install pyinstaller
pyinstaller --onefile --windowed --name ClawVoice --icon=assets/icon.ico run.py
```

---

## Contributing

PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

*Built by the Birbus Team — open source forever.*
