# Building ClawVoice Android APK

## Easiest — Download prebuilt APK
Download the latest `.apk` directly from [releases](https://github.com/birbusTeam-oss/ClawVoice/releases/latest). No build needed.

---

## Build from source (developers)

### Prerequisites
- Android Studio (latest)
- Android SDK 35
- Java 17+

### Steps
1. Clone the repo: `git clone https://github.com/birbusTeam-oss/ClawVoice`
2. Open Android Studio → **File → Open** → select the `android/` folder
3. Wait for Gradle sync to complete
4. Connect your Android phone via USB (USB debugging on) or start an emulator
5. Click **Run ▶** — builds and installs automatically

### Build a release APK
1. **Build → Generate Signed Bundle/APK → APK**
2. Create a keystore (save it safely — needed for all future updates)
3. APK appears at `android/app/release/app-release.apk`

---

## Install on your phone (sideload)
1. Transfer the `.apk` to your phone (USB, Google Drive, etc.)
2. **Settings → Security → Install unknown apps** → enable for your file manager
3. Tap the `.apk` to install
4. Open ClawVoice, enter your Anthropic API key, grant permissions
