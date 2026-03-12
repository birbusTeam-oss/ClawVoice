!define APP_NAME "ClawVoice"
!define APP_VERSION "0.7.2"
!define APP_EXE "ClawVoice.exe"

VIProductVersion "0.7.2.0"
VIAddVersionKey "ProductName" "ClawVoice"
VIAddVersionKey "CompanyName" "Birbus Team"
VIAddVersionKey "FileDescription" "ClawVoice - Voice Dictation for Windows"
VIAddVersionKey "FileVersion" "0.7.2"
VIAddVersionKey "ProductVersion" "0.7.2"
VIAddVersionKey "LegalCopyright" "MIT License"

Name "${APP_NAME} ${APP_VERSION}"
OutFile "ClawVoice-Setup.exe"
; Install to user's local app data — no admin required
InstallDir "$LOCALAPPDATA\${APP_NAME}"
RequestExecutionLevel user
SetCompressor lzma

!include "MUI2.nsh"
!define MUI_ABORTWARNING
!define MUI_ICON "assets\icon.ico"
!define MUI_UNICON "assets\icon.ico"

; Skip directory page — just install
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\${APP_EXE}"
!define MUI_FINISHPAGE_RUN_TEXT "Launch ClawVoice"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Install"
    ; Kill any running instance first
    nsExec::ExecToLog 'taskkill /F /IM ${APP_EXE}'

    ; Wipe old config for fresh install
    RMDir /r "$APPDATA\ClawVoice"

    ; Copy files
    SetOutPath "$INSTDIR"
    File "dist\${APP_EXE}"

    ; Start Menu
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"

    ; Desktop shortcut
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"

    ; Run on Windows startup
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "${APP_NAME}" '"$INSTDIR\${APP_EXE}"'

    ; Uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"

    ; Add/Remove Programs (user-level)
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "Birbus Team"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayIcon" "$INSTDIR\${APP_EXE}"
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1

    ; Store install dir
    WriteRegStr HKCU "Software\${APP_NAME}" "InstallDir" "$INSTDIR"
SectionEnd

Section "Uninstall"
    nsExec::ExecToLog 'taskkill /F /IM ${APP_EXE}'

    Delete "$INSTDIR\${APP_EXE}"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir "$INSTDIR"
    Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk"
    RMDir "$SMPROGRAMS\${APP_NAME}"
    Delete "$DESKTOP\${APP_NAME}.lnk"
    DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "${APP_NAME}"
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
    DeleteRegKey HKCU "Software\${APP_NAME}"
    RMDir /r "$APPDATA\ClawVoice"
SectionEnd
