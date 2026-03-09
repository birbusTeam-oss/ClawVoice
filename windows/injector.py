"""
Text injection — Win32 native clipboard + SendInput.
Saves and restores clipboard so user never loses their content.
"""
import time
import ctypes
import ctypes.wintypes


def inject(text: str):
    if not text or not text.strip():
        return
    try:
        _inject_win32(text)
    except Exception as e:
        print(f"Win32 inject failed: {e}")
        try:
            import pyperclip, subprocess
            pyperclip.copy(text)
            time.sleep(0.1)
            subprocess.run(['powershell', '-command',
                '$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys("^v")'],
                capture_output=True)
        except Exception as e2:
            print(f"Fallback inject failed: {e2}")


def _inject_win32(text: str):
    import win32clipboard, win32con

    # --- Save existing clipboard content ---
    saved_text = None
    try:
        win32clipboard.OpenClipboard()
        try:
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                saved_text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
        finally:
            win32clipboard.CloseClipboard()
    except Exception:
        pass

    # --- Set our text ---
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
    finally:
        win32clipboard.CloseClipboard()

    time.sleep(0.15)

    # --- SendInput Ctrl+V ---
    VK_CONTROL, VK_V = 0x11, 0x56
    KEYEVENTF_KEYUP = 0x0002
    INPUT_KEYBOARD = 1

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", ctypes.wintypes.WORD), ("wScan", ctypes.wintypes.WORD),
                    ("dwFlags", ctypes.wintypes.DWORD), ("time", ctypes.wintypes.DWORD),
                    ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

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

    inputs = [key_event(VK_CONTROL), key_event(VK_V),
              key_event(VK_V, KEYEVENTF_KEYUP), key_event(VK_CONTROL, KEYEVENTF_KEYUP)]
    arr = (INPUT * 4)(*inputs)
    ctypes.windll.user32.SendInput(4, arr, ctypes.sizeof(INPUT))

    # --- Restore clipboard after short delay ---
    time.sleep(0.2)
    if saved_text is not None:
        try:
            win32clipboard.OpenClipboard()
            try:
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(saved_text, win32con.CF_UNICODETEXT)
            finally:
                win32clipboard.CloseClipboard()
        except Exception:
            pass
