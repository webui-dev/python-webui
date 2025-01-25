# webui.py
from __future__ import annotations
from typing import Callable, Optional
from ctypes import *

# Import all the raw bindings
import webui_bindings as _raw

# == Enums ====================================================================


Browser     = _raw.WebuiBrowser
Runtime     = _raw.WebuiRuntime
EventType   = _raw.WebuiEvent
Config      = _raw.WebuiConfig


# == Definitions ==============================================================

# Global to hold Python callbacks
_py_bindings = {}

# -- JavaScript responses -----------------------
class JavaScript:
    error = False
    response = ""

# -- dispatcher for function bindings -----------
@_raw.CFUNCTYPE(None, _raw.POINTER(_raw.WebuiEventT))
def _dispatcher(c_event_ptr):
    """Global dispatcher for events."""
    event = c_event_ptr.contents
    if event.bind_id in _py_bindings:
        pyfunc = _py_bindings[event.bind_id]
        pyfunc(Event(event))


# -- Event Object -------------------------------
class Event:
    """Pythonic wrapper around webui_event_t."""
    __slots__ = ("window", "event_type", "element", "event_number", "bind_id",
                 "client_id", "connection_id", "cookies")

    def __init__(self, c_event: _raw.WebuiEventT):
        self.window        = c_event.window
        self.event_type    = c_event.event_type
        self.element       = c_event.element.decode('utf-8') if c_event.element else ''
        self.event_number  = c_event.event_number
        self.bind_id       = c_event.bind_id
        self.client_id     = c_event.client_id
        self.connection_id = c_event.connection_id
        self.cookies       = c_event.cookies.decode('utf-8') if c_event.cookies else ''

    def get_string_at(self, index: int) -> str:
        return _raw.webui_get_string_at(byref(self._c_event()), index).decode('utf-8')

    def _c_event(self) -> _raw.WebuiEventT:
        """Rebuild the underlying C struct if needed."""
        return _raw.WebuiEventT(
            window=self.window,
            event_type=self.event_type,
            element=self.element.encode('utf-8'),
            event_number=self.event_number,
            bind_id=self.bind_id,
            client_id=self.client_id,
            connection_id=self.connection_id,
            cookies=self.cookies.encode('utf-8')
        )


# -- Window Object ------------------------------
class Window:
    """
    Pythonic wrapper around a WebUI window.
    """
    def __init__(self, window_id: Optional[int] = None):
        """
        If window_id is None, we call webui_new_window().
        Otherwise, we call webui_new_window_id(window_id).
        """
        if window_id is None:
            self._id = _raw.webui_new_window()
        else:
            self._id = _raw.webui_new_window_id(window_id)

        if not self._id:
            raise RuntimeError("Failed to create a new WebUI window.")

        # A dictionary to hold Python function references
        # mapping: bind_id -> python_function
        # _py_bindings = {}

    @property
    def id(self) -> int:
        """Returns the internal C-level window id."""
        return self._id

    def show(self, content: str) -> bool:
        """
        Show or refresh the window with the specified content
        (HTML, URL, or local file).
        """
        # We pass UTF-8 strings to the C function
        return bool(_raw.webui_show(self._id, content.encode("utf-8")))

    def show_browser(self, content: str, browser: Browser) -> bool:
        """
        Show or refresh the window using a specific browser (by enum).
        """
        return bool(_raw.webui_show_browser(
            self._id, content.encode("utf-8"), c_size_t(browser.value)
        ))

    def bind(self, element: str, callback: Callable[[Event], None]) -> int:
        """
        Bind an HTML element and a JavaScript object with
        a backend function. Empty element name means all events.
        """
        element_c = element.encode('utf-8') if element else None
        bind_id = _raw.webui_bind(self._id, element_c, _dispatcher)
        _py_bindings[bind_id] = callback
        return bind_id

    def close(self) -> None:
        """
        Close this window (all clients).
        """
        _raw.webui_close(self._id)

    def destroy(self) -> None:
        """
        Close this window and free all memory resources used by it.
        """
        _raw.webui_destroy(self._id)

    def is_shown(self) -> bool:
        """Return True if the window is currently shown."""
        return bool(_raw.webui_is_shown(self._id))

    def set_kiosk(self, status: bool) -> None:
        """
        Set or unset kiosk (fullscreen) mode.
        """
        _raw.webui_set_kiosk(self._id, status)

    def run(self, script: str) -> None:
        """
        Run JavaScript in the window without waiting for a return.
        """
        _raw.webui_run(self._id, script.encode("utf-8"))

    def get_url(self) -> str:
        """
        Get the current URL as a string.
        """
        ptr = _raw.webui_get_url(self._id)
        if not ptr:
            return ""
        return ptr.decode("utf-8", errors="ignore")

    def set_size(self, width: int, height: int) -> None:
        _raw.webui_set_size(self._id, width, height)

    def script(self, script: str, timeout: int = 0, buffer_size: int = 4096) -> JavaScript:
        """
        Run JavaScript in single-client mode and return the result as a string.
        If there's an execution error or an empty response, returns None.

        :param script:   The JavaScript to run (e.g. "return 4 + 6;")
        :param timeout:  The time in seconds to wait for JS execution. 0 means no limit.
        :param buffer_size:  The size of the local buffer that will store the result.

        :return: The response from JavaScript as a string, or None if error or empty.
        """
        # Create a mutable buffer in which the C function can store the result
        buffer = create_string_buffer(buffer_size)

        # Call the raw C function
        success = _raw.webui_script(
            self._id,
            script.encode('utf-8'),   # Convert Python str -> bytes
            timeout,
            buffer,
            buffer_size
        )

        # Initializing Result
        res = JavaScript()

        res.data = buffer.value.decode('utf-8', errors='ignore')
        res.error = not success
        return res
    # TODO: left off here - 'AttributeError: 'int' object has no attribute 'script''




# -- Global functions below ---------------------
def wait() -> None:
    """Wait until all opened windows get closed."""
    _raw.webui_wait()

def exit() -> None:
    """Close all open windows and break out of webui_wait()."""
    _raw.webui_exit()

def is_high_contrast() -> bool:
    """Return True if the OS is using a high-contrast theme."""
    return bool(_raw.webui_is_high_contrast())



