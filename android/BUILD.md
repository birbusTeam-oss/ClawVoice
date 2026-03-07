# Building ClawVoice Android APK

## Prerequisites
- Android Studio (latest)
- Android SDK 35
- Java 17+

## Steps
1. Open Android Studio
2. File → Open → select the `android/` folder
3. Wait for Gradle sync
4. Build → Generate Signed Bundle/APK
5. Choose APK
6. Create new keystore (save it safely — you need it for all future updates)
7. Build → the APK appears in `android/app/release/`

## Install on your phone (sideload)
1. Transfer APK to your phone
2. Settings → Install unknown apps → allow your file manager
3. Tap the APK to install

## Note
Enable "Install from unknown sources" in Android Settings → Security
