import webui_bindings as _low

# webui.py
from . import webui_bindings as _low

# == Enums ====================================================================

Browser = _low.WebuiBrowser


class Window:
    """A Pythonic wrapper around a single WebUI window."""
    def __init__(self):
        self._id = _low.webui_new_window()
        if not self._id:
            raise RuntimeError("Failed to create WebUI window")

    def show(self, content: str) -> bool:
        """
        Show a window using either an HTML string, a filename, or a URL.

        :param self:      The window number returned by new_window().
        :param content:   The HTML/URL/file path (normal Python string).
        :return:          True if successful.
        """
        content_bytes = content.encode("utf-8")
        return bool(_low.webui_show(self._id, content_bytes))

    def show_browser(self, content: str, browser: Browser) -> bool:
        content_bytes = content.encode("utf-8")
        return bool(_low.webui_show_browser(self._id, content_bytes, int(browser)))

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


def main():
    w = Window()
    w.show("<h1>Hello from Python</h1>")

    # If they want to specify a browser:
    w.show_browser("index.html", Browser.Firefox)

    wait()