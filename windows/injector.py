"""
Text injection — clipboard paste via pyperclip + keypress simulation.
Simple and reliable. No ctypes struct issues.
"""
import time


def inject(text: str):
    """Inject text into the currently focused window."""
    if not text or not text.strip():
        return

    try:
        import pyperclip

        # Save current clipboard
        try:
            saved = pyperclip.paste()
        except Exception:
            saved = None

        # Set our text
        pyperclip.copy(text)
        time.sleep(0.1)

        # Simulate Ctrl+V using pynput (reliable, no struct issues)
        from pynput.keyboard import Key, Controller
        kb = Controller()
        kb.press(Key.ctrl)
        kb.press('v')
        time.sleep(0.05)
        kb.release('v')
        kb.release(Key.ctrl)

        # Restore clipboard after paste completes
        time.sleep(0.3)
        if saved is not None:
            try:
                pyperclip.copy(saved)
            except Exception:
                pass

    except Exception as e:
        print(f"Inject failed: {e}")
