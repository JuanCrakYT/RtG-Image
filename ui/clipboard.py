import pyperclip


def copy_text_to_clipboard(text: str) -> bool:
    try:
        pyperclip.copy(text)
        return True
    except Exception:
        return False
