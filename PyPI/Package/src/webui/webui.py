import webui_bindings as _low

# webui.py
from . import webui_bindings as _low



class Window:
    """A Pythonic wrapper around a single WebUI window."""
    def __init__(self):
        self._id = _low.webui_new_window()
        if not self._id:
            raise RuntimeError("Failed to create WebUI window")

    def show(self, content: str) -> bool:
        content_bytes = content.encode("utf-8")
        return bool(_low.webui_show(self._id, content_bytes))

    def close(self) -> None:
        _low.webui_close(self._id)


# ---- Global-style functions below ----
def wait() -> None:
    """Wait until all opened windows get closed."""
    _low.webui_wait()

def exit() -> None:
    """Close all open windows and break out of webui_wait()."""
    _low.webui_exit()

def is_high_contrast() -> bool:
    """Return True if the OS is using a high-contrast theme."""
    return bool(_low.webui_is_high_contrast())