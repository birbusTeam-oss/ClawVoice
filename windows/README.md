# ClawVoice for Windows 🖥️

Hold **Ctrl+Space** → speak → release → text appears wherever you're typing.

No Python. No installation. Just download and run.

---

## Download & Run

1. Download **ClawVoice.exe** from [github.com/birbusTeam-oss/ClawVoice/releases/latest](https://github.com/birbusTeam-oss/ClawVoice/releases/latest)
2. Double-click `ClawVoice.exe`
3. If Windows shows a security warning → click **More info → Run anyway**
4. ClawVoice appears in your system tray (bottom right corner)
5. Right-click tray icon → **Settings**
6. Paste your Anthropic API key → **Save**
7. Hold **Ctrl+Space** anywhere to start dictating

---

## Get your API key

Free at [console.anthropic.com](https://console.anthropic.com) — that's the only key you need.

---

## How it works

1. Hold **Ctrl+Space** — mic starts recording (tray turns 🔴 red)
2. Release **Ctrl+Space** — recording stops (tray turns 🟡 yellow while transcribing)
3. Claude transcribes and cleans up your speech
4. Text is typed into whatever field you were in

> 🟣 Tray icon is **purple** when idle · **red** while recording · **yellow** while transcribing

---

## Privacy

Your audio goes directly from your mic to Anthropic's API. We have no servers. We store nothing.

---

## For developers — build from source

```bash
git clone https://github.com/birbusTeam-oss/ClawVoice
cd windows
pip install -r requirements.txt
python run.py

# Build your own .exe
pip install pyinstaller
pyinstaller --onefile --windowed --name ClawVoice run.py
```
