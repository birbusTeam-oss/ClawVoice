import pyperclip
import keyboard
import time

class TextInjector:
    """
    Injects transcribed text into whatever app/field is currently focused.
    Uses clipboard + Ctrl+V for maximum compatibility across all apps.
    """

    def inject(self, text: str):
        if not text:
            return
        try:
            # Save current clipboard
            try:
                original_clipboard = pyperclip.paste()
            except:
                original_clipboard = ""

            # Put our text in clipboard
            pyperclip.copy(text)
            time.sleep(0.05)  # Brief delay for clipboard to settle

            # Paste into focused field
            keyboard.send("ctrl+v")
            time.sleep(0.1)

            # Optionally restore original clipboard after 2 seconds
            # (don't restore immediately or paste won't work)

        except Exception as e:
            print(f"Injection error: {e}")
