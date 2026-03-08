@echo off
echo Building ClawVoice installer...

REM Check if NSIS is installed
where makensis >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    makensis installer.nsi
    echo Installer built: ClawVoice-Setup.exe
) else (
    echo NSIS not found — creating portable zip instead
    powershell Compress-Archive -Path dist\ClawVoice.exe -DestinationPath dist\ClawVoice-portable.zip
    echo Portable zip created: dist\ClawVoice-portable.zip
)
