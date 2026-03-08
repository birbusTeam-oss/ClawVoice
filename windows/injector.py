"""
Text injection for Windows — uses native Win32 clipboard + SendInput.
Most reliable method across all Windows apps.
"""
import time
import ctypes
import ctypes.wintypes

def inject(text: str):
    if not text or not text.strip():
        return

    try:
        # Method 1: Win32 native clipboard + paste
        _inject_win32(text)
    except Exception as e:
        print(f"Win32 inject failed: {e}")
        try:
            # Method 2: pyperclip fallback
            import pyperclip
            import subprocess
            pyperclip.copy(text)
            time.sleep(0.1)
            subprocess.run(['powershell', '-command',
                '$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys("^v")'],
                capture_output=True)
        except Exception as e2:
            print(f"Fallback inject failed: {e2}")

def _inject_win32(text: str):
    """Use Win32 API to set clipboard and send Ctrl+V"""
    import win32clipboard
    import win32con
    import win32api

    # Set clipboard
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
    finally:
        win32clipboard.CloseClipboard()

    time.sleep(0.15)  # Let clipboard settle

    # Send Ctrl+V using SendInput (more reliable than keybd_event)
    VK_CONTROL = 0x11
    VK_V = 0x56
    KEYEVENTF_KEYUP = 0x0002

    INPUT_KEYBOARD = 1

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", ctypes.wintypes.WORD),
            ("wScan", ctypes.wintypes.WORD),
            ("dwFlags", ctypes.wintypes.DWORD),
            ("time", ctypes.wintypes.DWORD),
            ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
        ]

    class INPUT(ctypes.Structure):
        class _INPUT(ctypes.Union):
            _fields_ = [("ki", KEYBDINPUT)]
        _anonymous_ = ("_input",)
        _fields_ = [("type", ctypes.wintypes.DWORD), ("_input", _INPUT)]

    def key_event(vk, flags=0):
        inp = INPUT()
        inp.type = INPUT_KEYBOARD
        inp.ki.wVk = vk
        inp.ki.dwFlags = flags
        inp.ki.dwExtraInfo = ctypes.cast(ctypes.pointer(ctypes.c_ulong(0)),
                                          ctypes.POINTER(ctypes.c_ulong))
        return inp

    inputs = [
        key_event(VK_CONTROL),           # Ctrl down
        key_event(VK_V),                  # V down
        key_event(VK_V, KEYEVENTF_KEYUP), # V up
        key_event(VK_CONTROL, KEYEVENTF_KEYUP), # Ctrl up
    ]

    arr = (INPUT * len(inputs))(*inputs)
    ctypes.windll.user32.SendInput(len(inputs), arr, ctypes.sizeof(INPUT))
