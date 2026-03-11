"""
Text injection — clipboard paste via pynput keypress simulation.
Controller is pre-initialized to avoid first-use conflicts with keyboard library.
"""
import time

# Pre-initialize pynput Controller at import time
# This prevents first-use crash when keyboard library hook is active
_controller = None

def _get_controller():
    global _controller
    if _controller is None:
        from pynput.keyboard import Controller
        _controller = Controller()
    return _controller


def inject(text: str):
    """Inject text into the currently focused window via clipboard paste."""
    if not text or not text.strip():
        return

    try:
        import pyperclip
        from pynput.keyboard import Key

        kb = _get_controller()

        # Save current clipboard
        try:
            saved = pyperclip.paste()
        except Exception:
            saved = None

        # Set our text to clipboard
        pyperclip.copy(text)
        time.sleep(0.15)

        # Simulate Ctrl+V paste
        kb.press(Key.ctrl)
        time.sleep(0.03)
        kb.press('v')
        time.sleep(0.05)
        kb.release('v')
        time.sleep(0.03)
        kb.release(Key.ctrl)

        # Restore clipboard after paste completes
        time.sleep(0.4)
        if saved is not None:
            try:
                pyperclip.copy(saved)
            except Exception:
                pass

    except Exception as e:
        print(f"Inject failed: {e}")
