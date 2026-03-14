# ClawVoice Status — 2026-03-13

## Current Version: v0.7.3

## Working
- ✅ Background startup (no welcome screen)
- ✅ Ctrl+Alt hotkey → record → transcribe → inject
- ✅ System tray with "Initializing..." → "Ready" notifications
- ✅ Flag-based architecture (pynput → flags → QTimer → Qt)
- ✅ Thread-safe logging (Qt signals for widget updates)
- ✅ User-level installer (%LOCALAPPDATA%)
- ✅ Start with Windows (auto-enabled)
- ✅ 0.5s tail buffer for trailing words
- ✅ Transcription logging toggle

## Known Issues
- ⚠️ Smart App Control blocks unsigned exe (need code signing cert ~$200-300/yr)
- ⚠️ Test Build CI workflow still failing (doesn't block releases)

## Next
- [ ] Validate v0.7.3 stability (tail buffer + logging)
- [ ] Code signing certificate
- [ ] macOS port (Swift)
- [ ] Linux port (Python native)
