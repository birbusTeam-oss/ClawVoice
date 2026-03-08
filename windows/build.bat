@echo off
echo ========================================
echo  ClawVoice Windows Build Script
echo ========================================
echo.
echo Installing dependencies...
pip install pyinstaller PyQt6 keyboard pyaudio requests pynput pyperclip anthropic pystray Pillow
echo.
echo Building ClawVoice.exe...
pyinstaller --onefile --windowed --name ClawVoice --icon=NONE run.py
echo.
if exist dist\ClawVoice.exe (
    echo ✅ SUCCESS! ClawVoice.exe is ready at:
    echo    dist\ClawVoice.exe
    echo.
    echo Copy it anywhere and double-click to run.
) else (
    echo ❌ Build failed. Check errors above.
)
pause
