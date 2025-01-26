# webui.py
from __future__ import annotations
from typing import Callable, Optional
from ctypes import *

# Import all the raw bindings
import webui_bindings as _raw

# Define the C function type for the file handler
filehandler_callback = CFUNCTYPE(
    c_void_p,               # Return type: pointer to the HTTP response bytes
    c_char_p,               # filename: const char*
    POINTER(c_int)          # length: int*
)

# == Enums ====================================================================


Browser     = _raw.WebuiBrowser
Runtime     = _raw.WebuiRuntime
EventType   = _raw.WebuiEvent
Config      = _raw.WebuiConfig


# == Definitions ==============================================================


# -- JavaScript responses -----------------------
class JavaScript:
    error = False
    response = ""


# -- Event Object -------------------------------
class Event:
    """Pythonic wrapper around webui_event_t."""
    __slots__ = ("window", "event_type", "element", "event_number", "bind_id",
                 "client_id", "connection_id", "cookies")

    def __init__(self, win: Window, c_event: _raw.WebuiEventT):
        self.window        = win
        self.event_type    = c_event.event_type
        self.element       = c_event.element.decode('utf-8') if c_event.element else ''
        self.event_number  = c_event.event_number
        self.bind_id       = c_event.bind_id
        self.client_id     = c_event.client_id
        self.connection_id = c_event.connection_id
        self.cookies       = c_event.cookies.decode('utf-8') if c_event.cookies else ''

    def _c_event(self) -> _raw.WebuiEventT:
        """Rebuild the underlying C struct if needed."""
        return _raw.WebuiEventT(
            window=c_size_t(self.window.get_window_id),
            event_type=self.event_type,
            element=self.element.encode('utf-8'),
            event_number=self.event_number,
            bind_id=self.bind_id,
            client_id=self.client_id,
            connection_id=self.connection_id,
            cookies=self.cookies.encode('utf-8')
        )

    def show_client(self, content: str) -> bool:
        return bool(_raw.webui_show_client(self._c_event(), content.encode('utf-8')))

    def close_client(self):
        _raw.webui_close_client(self._c_event())

    def get_string_at(self, index: int) -> str:
        """
        Retrieve a string argument from the underlying C event data at a given index.

        Args:
            index (int): The index of the string argument to retrieve.

        Returns:
            str: The UTF-8 decoded string corresponding to the specified index.
        """
        return _raw.webui_get_string_at(byref(self._c_event()), index).decode('utf-8')



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
            self._window: int = _raw.webui_new_window()
        else:
            self._window: int = _raw.webui_new_window_id(window_id)

        if not self._window:
            raise RuntimeError("Failed to create a new WebUI window.")

        self._window_id: str = str(self._window)

        callback_function_type = _raw.CFUNCTYPE(None, _raw.POINTER(_raw.WebuiEventT))
        self._dispatcher_cfunc = callback_function_type(self._make_dispatcher())
        # Dict to keep track of binded functions: {bind_id: python_function}
        self._cb_func_list: dict = {}

        self._file_handler_cfunc = None

    # -- dispatcher for function bindings -----------
    def _make_dispatcher(self):
        """Return a function that matches CFUNCTYPE signature but closes over `self`."""
        def dispatcher(c_event_ptr):
            event = c_event_ptr.contents
            if event.bind_id in self._cb_func_list:
                pyfunc = self._cb_func_list[event.bind_id]
                pyfunc(Event(self, event))

        return dispatcher

    @property
    def get_window_id(self) -> int:
        """Returns the window id."""
        return self._window

    def bind(self, element: str, func: Callable[[Event], None]) -> int:
        """
        Bind an HTML element and a JavaScript object with
        a backend function. Empty element name means all events.
        """
        element_c = element.encode('utf-8') if element else None
        bind_id = _raw.webui_bind(self._window, element_c, self._dispatcher_cfunc)
        self._cb_func_list[bind_id] = func
        return bind_id

    def get_best_browser(self) -> Browser:
        """
        Get the recommended web browser to use. If you
        are already using one, this function will return the same browser.
        """
        return Browser(int(_raw.webui_get_best_browser(self._window)))

    def show(self, content: str) -> bool:
        """
        Show or refresh the window with the specified content
        (HTML, URL, or local file).
        """
        # We pass UTF-8 strings to the C function
        return bool(_raw.webui_show(self._window, content.encode("utf-8")))

    def show_browser(self, content: str, browser: Browser) -> bool:
        """
        Show or refresh the window using a specific browser (by enum).
        """
        return bool(_raw.webui_show_browser(self._window, content.encode("utf-8"), c_size_t(browser.value)))

    def start_server(self, content: str) -> str:
        return _raw.webui_start_server(self._window, content.encode("utf-8")).decode("utf-8")

    def show_wv(self, content: str) -> bool:
        return bool(_raw.webui_show_wv(self._window, content.encode("utf-8")))

    def set_kiosk(self, status: bool) -> None:
        """
        Set or unset kiosk (fullscreen) mode.
        """
        _raw.webui_set_kiosk(self._window, c_bool(status))

    def set_high_contrast(self, status: bool) -> None:
        _raw.webui_set_high_contrast(self._window, c_bool(status))

    def close(self) -> None:
        """
        Close this window (all clients).
        """
        _raw.webui_close(self._window)

    def destroy(self) -> None:
        """
        Close this window and free all memory resources used by it.
        """
        _raw.webui_destroy(self._window)

    def set_root_folder(self, path: str) -> bool:
        return bool(_raw.webui_set_root_folder(self._window, path.encode("utf-8")))

    def set_file_handler(self, handler: Callable[[str], bytes]) -> None:
        """
        Set a custom file handler to serve files for this window.

        The custom handler must return a complete HTTP response (header + body)
        as bytes. This disables any previously set file handler for this window.

        Args:
            handler (Callable[[str], bytes]): A Python function that takes the
            requested filename as a string and returns the full HTTP response
            (including headers) as bytes.

        Returns:
            None
        """
        def _internal_file_handler(filename_ptr: c_char_p, length_ptr: POINTER(c_int)) -> c_void_p:
            """
            Internal C callback that matches the signature required by webui_set_file_handler.
            """
            # Decode the incoming filename from C
            filename = filename_ptr.decode('utf-8') if filename_ptr else ""

            # Call the Python-level handler to get the HTTP response
            response_bytes = handler(filename)

            # Create a ctypes buffer from the Python bytes; this buffer must remain alive
            # at least until WebUI is done with it.
            buf = create_string_buffer(response_bytes)

            # Set the length (the int* that C expects)
            length_ptr[0] = len(response_bytes)

            # Return a pointer (void*) to the buffer
            return cast(buf, c_void_p)

        # Keep a reference so it doesnt get garbage collected
        self._file_handler_cfunc = filehandler_callback(_internal_file_handler)

        _raw.webui_set_file_handler(self._window, self._file_handler_cfunc)

    # TODO: set_file_handler_window

    def is_shown(self) -> bool:
        """Return True if the window is currently shown."""
        return bool(_raw.webui_is_shown(self._window))

    def set_icon(self, icon: str, icon_type: str) -> None:
        _raw.webui_set_icon(self._window, icon.encode("utf-8"), icon_type.encode("utf-8"))

    def run(self, script: str) -> None:
        """
        Run JavaScript in the window without waiting for a return.
        """
        _raw.webui_run(self._window, script.encode("utf-8"))

    def get_url(self) -> str:
        """
        Get the current URL as a string.
        """
        ptr = _raw.webui_get_url(self._window)
        if not ptr:
            return ""
        return ptr.decode("utf-8", errors="ignore")

    def set_size(self, width: int, height: int) -> None:
        _raw.webui_set_size(self._window, width, height)

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
            self._window,
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



# -- Global functions below ---------------------
def get_new_window_id() -> int:
    return int(_raw.webui_get_new_window_id)

def is_high_contrast() -> bool:
    """Return True if the OS is using a high-contrast theme."""
    return bool(_raw.webui_is_high_contrast())

def browser_exist(browser: Browser) -> bool:
    return bool(_raw.webui_browser_exist(c_size_t(browser.value)))

def wait() -> None:
    """Wait until all opened windows get closed."""
    _raw.webui_wait()

def exit() -> None:
    """Close all open windows and break out of webui_wait()."""
    _raw.webui_exit()

def set_default_root_folder(path: str) -> bool:
    return bool(_raw.webui_set_default_root_folder(path.encode("utf-8")))

def set_timeout(seconds: int) -> None:
    _raw.webui_set_timeout(c_size_t(seconds))