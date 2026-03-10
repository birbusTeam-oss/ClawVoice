# ClawVoice

Voice dictation for Windows. Hold a hotkey, speak, release — text appears wherever your cursor is.

Built by the Birbus Team. Open source, MIT license. Zero servers. Your API key stays on your device.

---

## Download & Install

1. Go to [Releases](https://github.com/birbusTeam-oss/ClawVoice/releases/latest)
2. Download **ClawVoice-Setup.exe**
3. Run the installer
4. On first launch, enter your [Anthropic API key](https://console.anthropic.com/) — it's stored locally, never sent anywhere
5. ClawVoice starts in your system tray

## How to use

- **Hold Ctrl+Alt** to start recording
- **Speak**
- **Release Ctrl+Alt** — your words are transcribed and typed into the active window

Works in any app: browsers, editors, chat, email, anywhere.

> 🟣 Tray icon: **purple** = idle · **red** = recording · **yellow** = transcribing

## Requirements

- Windows 10 or 11
- A microphone
- An [Anthropic API key](https://console.anthropic.com/) (you pay Anthropic directly — ~$0.001 per transcription)

## Privacy

- No accounts, no servers, no telemetry
- Your audio is sent directly to Anthropic's API and immediately discarded
- Your API key is stored locally in `%APPDATA%\ClawVoice\config.json`

## Building from source

```bash
cd windows
pip install -r requirements.txt
python run.py
```

To build the installer:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name ClawVoice --icon=assets/icon.ico run.py
makensis installer.nsi
```

## Contributing

PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE)
