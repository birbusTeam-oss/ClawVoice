@echo off
echo ========================================
echo  ClawVoice Windows Build
echo ========================================
echo.
echo Installing dependencies...
pip install pyinstaller PyQt6 keyboard pyaudio requests pynput pyperclip anthropic pystray Pillow pywin32
echo.
echo Building ClawVoice.exe...
pyinstaller --onefile --windowed --name ClawVoice --icon=assets/icon.ico --add-data "assets;assets" run.py
echo.
if exist dist\ClawVoice.exe (
    echo SUCCESS: dist\ClawVoice.exe
) else (
    echo FAILED. Check errors above.
)
pause
