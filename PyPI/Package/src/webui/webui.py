# webui.py
from __future__ import annotations
from typing import Callable, Optional
from ctypes import *

# Import all the raw bindings
import webui_bindings as _raw

# The C function type for the file handler
filehandler_callback = CFUNCTYPE(
    c_void_p,               # Return type: pointer to the HTTP response bytes
    c_char_p,               # filename: const char*
    POINTER(c_int)          # length: int*
)

# C function type for the file handler window
filehandler_window_callback = CFUNCTYPE(
    c_size_t,
    c_void_p,
    c_char_p,
    POINTER(c_int)
)

# == Enums ====================================================================


Browser     = _raw.WebuiBrowser
"""
NoBrowser      = 0  - No web browser
AnyBrowser     = 1  - Default recommended web browser
Chrome         = 2  - Google Chrome
Firefox        = 3  - Mozilla Firefox
Edge           = 4  - Microsoft Edge
Safari         = 5  - Apple Safari
Chromium       = 6  - The Chromium Project
Opera          = 7  - Opera Browser
Brave          = 8  - The Brave Browser
Vivaldi        = 9  - The Vivaldi Browser
Epic           = 10 - The Epic Browser
Yandex         = 11 - The Yandex Browser
ChromiumBased  = 12 - Any Chromium based browser
Webview        = 13 - WebView (Non-web-browser)
"""

Runtime     = _raw.WebuiRuntime
"""
NoRuntime = 0 - Prevent WebUI from using any runtime for .js and .ts files
Deno      = 1 - Use Deno runtime for .js and .ts files
NodeJS    = 2 - Use Nodejs runtime for .js files
Bun       = 3 - Use Bun runtime for .js and .ts files
"""

EventType   = _raw.WebuiEvent
"""
DISCONNECTED = 0 - Window disconnection event
CONNECTED    = 1 - Window connection event
MOUSE_CLICK  = 2 - Mouse click event
NAVIGATION   = 3 - Window navigation event
CALLBACK     = 4 - Function call event
"""

Config      = _raw.WebuiConfig
"""
show_wait_connection = 0:
    Control if 'webui_show()', 'webui_show_browser()' and
    'webui_show_wv()' should wait for the window to connect
    before returns or not.
    Default: True
    

ui_event_blocking = 1:
    Control if WebUI should block and process the UI events
    one a time in a single thread `True`, or process every
    event in a new non-blocking thread `False`. This updates
    all windows. You can use `webui_set_event_blocking()` for
    a specific single window update.
    Default: False


folder_monitor = 2:
    Automatically refresh the window UI when any file in the
    root folder gets changed.
    Default: False


multi_client = 3:   
    Allow multiple clients to connect to the same window,
    This is helpful for web apps (non-desktop software),
    Please see the documentation for more details.
    Default: False
    

use_cookies = 4:
    Allow or prevent WebUI from adding `webui_auth` cookies.
    WebUI uses these cookies to identify clients and block
    unauthorized access to the window content using a URL.
    Please keep this option to `True` if you want only a single
    client to access the window content.
    Default: True
    

asynchronous_response = 5:
    If the backend uses asynchronous operations, set this
    option to `True`. This will make webui wait until the
    backend sets a response using `webui_return_x()`.
"""


# == Definitions ==============================================================


# -- JavaScript responses -----------------------
class JavaScript:
    """
    A return response type for functions dealing with JavaScript.
    """
    error = False
    response = ""


# -- Event Object -------------------------------
class Event:
    """
    WebUI Event Object

    Caries most of the client-side functions but also caries has reference to
    the Window object to be able to call Window related functions if needed.
    """
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
        """
        Rebuild of the underlying C struct for interacting with the C API
        """
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

    # -- show_client --------------------------------
    def show_client(self, content: str) -> bool:
        """
        Display content in the client interface.

        Args:
            content (str): The content to be displayed in the client, encoded in UTF-8.

        Returns:
            bool: True if the content was successfully displayed, False otherwise.
        """
        return bool(_raw.webui_show_client(byref(self._c_event()), content.encode('utf-8')))

    # -- close_client -------------------------------
    def close_client(self) -> None:
        """
        Close the client interface.

        This method closes the currently active client interface associated with the event.

        Returns:
            None
        """
        _raw.webui_close_client(byref(self._c_event()))

    # -- send_raw_client ----------------------------
    def send_raw_client(self, function: str, raw: Optional[int], size: int) -> None:
        """
        Send raw data to the client for processing.

        Args:
            function (str): The name of the function to invoke on the client, encoded in UTF-8.
            raw (Optional[int]): A pointer to the raw data. Must not be `None`.
            size (int): The size of the raw data in bytes.

        Raises:
            ValueError: If `raw` is `None`.

        Returns:
            None
        """
        if raw is None:
            raise ValueError("Invalid Pointer: Cannot send a null pointer.")
        _raw.webui_send_raw_client(
            byref(self._c_event()),
            c_char_p(function.encode("utf-8")),
            c_void_p(raw),
            c_size_t(size)
        )

    # -- navigate_client ----------------------------
    def navigate_client(self, url: str) -> None:
        """
        Navigate the client to a specified URL.

        Args:
            url (str): The URL to navigate the client to, encoded in UTF-8.

        Returns:
            None
        """
        _raw.webui_navigate_client(byref(self._c_event()), c_char_p(url.encode("utf-8")))

    # -- run_client ---------------------------------
    def run_client(self, script: str) -> None:
        """
        Execute a script in the client.

        Args:
            script (str): The script to be executed in the client, encoded in UTF-8.

        Returns:
            None
        """
        _raw.webui_run_client(byref(self._c_event()), c_char_p(script.encode("utf-8")))

    # -- script_client ------------------------------
    def script_client(self, script: str, timeout: int = 0, buffer_size: int = 4096) -> JavaScript:
        """
        Execute a JavaScript script in the client and retrieve the result.

        Args:
            script (str): The JavaScript code to execute in the client, encoded in UTF-8.
            timeout (int, optional): The maximum time in milliseconds to wait for the script to execute. Defaults to 0 (no timeout).
            buffer_size (int, optional): The size of the buffer to store the result. Defaults to 4096.

        Returns:
            JavaScript: An object containing the result of the script execution. The `data` attribute contains the script output,
            and the `error` attribute indicates whether an error occurred (True if there was an error, False otherwise).
        """
        # Create a mutable buffer in which the C function can store the result
        buffer = create_string_buffer(buffer_size)

        # Call the raw C function
        success = _raw.webui_script_client(
            byref(self._c_event()),
            script.encode('utf-8'),
            timeout,
            buffer,
            buffer_size
        )

        # Initializing Result
        res = JavaScript()

        res.data = buffer.value.decode('utf-8', errors='ignore')
        res.error = not success
        return res

    # -- get_count ----------------------------------
    def get_count(self) -> int:
        """
        Retrieve how many arguments there are in an event.

        Returns:
            int: the number of arguments.
        """
        return int(_raw.webui_get_count(byref(self._c_event())))

    # -- get_int_at ---------------------------------
    def get_int_at(self, index: int) -> int:
        return int(_raw.webui_get_int_at(byref(self._c_event()), c_size_t(index)))

    # -- get_int ------------------------------------
    def get_int(self) -> int:
        return int(_raw.webui_get_int(byref(self._c_event())))

    # -- get_float_at -------------------------------
    def get_float_at(self, index: int) -> float:
        return float(_raw.webui_get_float_at(byref(self._c_event()), c_size_t(index)))

    # -- get_float ----------------------------------
    def get_float(self) -> float:
        return float(_raw.webui_get_float(byref(self._c_event())))

    # -- get_string_at ------------------------------
    def get_string_at(self, index: int) -> str:
        """
        Retrieve a string argument from the underlying C event data at a given index.

        Args:
            index (int): The index of the string argument to retrieve.

        Returns:
            str: The UTF-8 decoded string corresponding to the specified index.
        """
        char_ptr = _raw.webui_get_string_at(byref(self._c_event()), c_size_t(index))
        if char_ptr is None:
            return ""
        return str(char_ptr.decode("utf-8"))

    # -- get_string ---------------------------------
    def get_string(self) -> str:
        char_ptr = _raw.webui_get_string(byref(self._c_event()))
        if char_ptr is None:
            return ""
        return str(char_ptr.decode("utf-8"))

    # -- get_bool_at --------------------------------
    def get_bool_at(self, index: int) -> bool:
        return bool(_raw.webui_get_bool_at(byref(self._c_event()), c_size_t(index)))

    # -- get_bool -----------------------------------
    def get_bool(self) -> bool:
        return bool(_raw.webui_get_bool(byref(self._c_event())))

    # -- get_size_at --------------------------------
    def get_size_at(self, index: int) -> int:
        return int(_raw.webui_get_size_at(byref(self._c_event()), c_size_t(index)))

    # -- get_size -----------------------------------
    def get_size(self) -> int:
        return int(_raw.webui_get_size(byref(self._c_event())))

    # -- return_int ---------------------------------
    def return_int(self, n: int) -> None:
        _raw.webui_return_int(byref(self._c_event()), c_longlong(n))

    # -- return_float -------------------------------
    def return_float(self, f: float) -> None:
        _raw.webui_return_float(byref(self._c_event()), c_double(f))

    # -- return_string ------------------------------
    def return_string(self, s: str) -> None:
        _raw.webui_return_string(byref(self._c_event()), c_char_p(s.encode("utf-8")))

    # -- return_bool --------------------------------
    def return_bool(self, b: bool) -> None:
        _raw.webui_return_bool(byref(self._c_event()), c_bool(b))


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
            # -- new_window ---------------------------------
            self._window = int(_raw.webui_new_window())
        else:
            # -- new_window_id ------------------------------
            self._window = int(_raw.webui_new_window_id(window_id))

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
    # -- get_window_id --------------------------
    def get_window_id(self) -> int:
        """Returns the window id."""
        return self._window

    # -- bind ---------------------------------------
    def bind(self, element: str, func: Callable[[Event], None]) -> int:
        """
        Bind an HTML element and a JavaScript object with
        a backend function. Empty element name means all events.
        """
        element_c = element.encode('utf-8') if element else None
        bind_id = _raw.webui_bind(self._window, element_c, self._dispatcher_cfunc)
        self._cb_func_list[bind_id] = func
        return bind_id

    # -- get_best_browser ---------------------------
    def get_best_browser(self) -> Browser:
        """
        Get the recommended web browser to use. If you
        are already using one, this function will return the same browser.
        """
        return Browser(int(_raw.webui_get_best_browser(self._window)))

    # -- show ---------------------------------------
    def show(self, content: str) -> bool:
        """
        Show or refresh the window with the specified content
        (HTML, URL, or local file).
        """
        # We pass UTF-8 strings to the C function
        return bool(_raw.webui_show(self._window, content.encode("utf-8")))

    # -- show_browser -------------------------------
    def show_browser(self, content: str, browser: Browser) -> bool:
        """
        Show or refresh the window using a specific browser (by enum).
        """
        return bool(_raw.webui_show_browser(self._window, content.encode("utf-8"), c_size_t(browser.value)))

    # -- start_server -------------------------------
    def start_server(self, content: str) -> str:
        return _raw.webui_start_server(self._window, content.encode("utf-8")).decode("utf-8")

    # -- show_wv ------------------------------------
    def show_wv(self, content: str) -> bool:
        return bool(_raw.webui_show_wv(self._window, content.encode("utf-8")))

    # -- set_kiosk ----------------------------------
    def set_kiosk(self, status: bool) -> None:
        """
        Set or unset kiosk (fullscreen) mode.
        """
        _raw.webui_set_kiosk(self._window, c_bool(status))

    # -- set_high_contrast --------------------------
    def set_high_contrast(self, status: bool) -> None:
        _raw.webui_set_high_contrast(self._window, c_bool(status))

    # -- close --------------------------------------
    def close(self) -> None:
        """
        Close this window (all clients).
        """
        _raw.webui_close(self._window)

    # -- destroy ------------------------------------
    def destroy(self) -> None:
        """
        Close this window and free all memory resources used by it.
        """
        _raw.webui_destroy(self._window)

    # -- set_root_folder ----------------------------
    def set_root_folder(self, path: str) -> bool:
        return bool(_raw.webui_set_root_folder(self._window, path.encode("utf-8")))

    # -- set_file_handler----------------------------
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

    # -- set_file_handler_window --------------------
    # TODO: set_file_handler_window

    # -- is_shown -----------------------------------
    def is_shown(self) -> bool:
        """Return True if the window is currently shown."""
        return bool(_raw.webui_is_shown(self._window))

    # -- set_icon -----------------------------------
    def set_icon(self, icon: str, icon_type: str) -> None:
        _raw.webui_set_icon(self._window, icon.encode("utf-8"), icon_type.encode("utf-8"))

    # -- send_raw -----------------------------------
    def send_raw(self, function: str, raw: Optional[c_void_p], size: int) -> None:
        if raw is None:
            raise ValueError("Invalid pointer: Cannot send a null pointer.")
        _raw.webui_send_raw(
            c_size_t(self._window),
            c_char_p(function.encode("utf-8")),
            c_void_p(raw),
            c_size_t(size)
        )

    # -- set_hide -----------------------------------
    def set_hide(self, status: bool) -> bool:
        return bool(_raw.webui_set_hide(c_size_t(self._window), c_bool(status)))

    # -- set_size -----------------------------------
    def set_size(self, width: int, height: int) -> None:
        _raw.webui_set_size(c_size_t(self._window), c_uint(width), c_uint(height))

    # -- set_position -------------------------------
    def set_position(self, x: int, y: int) -> None:
        _raw.webui_set_position(c_size_t(self._window), c_uint(x), c_uint(y))

    # -- set_profile --------------------------------
    def set_profile(self, name: str, path: str) -> None:
        _raw.webui_set_profile(c_size_t(self._window), c_char_p(name.encode("utf-8")), c_char_p(path.encode("utf-8")))

    # -- set_proxy ----------------------------------
    def set_proxy(self, proxy_server: str) -> None:
        _raw.webui_set_proxy(c_size_t(self._window), c_char_p(proxy_server.encode("utf-8")))

    # -- get_url ------------------------------------
    def get_url(self) -> str:
        """
        Get the current URL as a string.
        """
        return _raw.webui_get_url(c_size_t(self._window)).decode("utf-8")

    # -- set_public ---------------------------------
    def set_public(self, status: bool) -> None:
        _raw.webui_set_public(c_size_t(self._window), c_bool(status))

    # -- navigate -----------------------------------
    def navigate(self, url: str) -> None:
        _raw.webui_navigate(c_size_t(self._window), c_char_p(url.encode("utf-8")))

    # -- delete_profile -----------------------------
    def delete_profile(self) -> None:
        _raw.webui_delete_profile(c_size_t(self._window))

    # -- get_parent_process_id ----------------------
    def get_parent_process_id(self) -> int:
        return int(_raw.webui_get_parent_process_id(c_size_t(self._window)))

    # -- get_child_process_id -----------------------
    def get_child_process_id(self) -> int:
        return int(_raw.webui_get_child_process_id(c_size_t(self._window)))

    # -- get_port -----------------------------------
    def get_port(self) -> int:
        return int(_raw.webui_get_port(c_size_t(self._window)))

    # -- set_port -----------------------------------
    def set_port(self, port: int) -> bool:
        return bool(_raw.webui_set_port(c_size_t(self._window), c_size_t(port)))

    # -- set_event_blocking -------------------------
    def set_event_blocking(self, status: bool) -> None:
        _raw.webui_set_event_blocking(c_size_t(self._window), c_bool(status))

    # -- run ----------------------------------------
    def run(self, script: str) -> None:
        """
        Run JavaScript in the window without waiting for a return.
        """
        _raw.webui_run(self._window, script.encode("utf-8"))

    # -- script -------------------------------------
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

    # -- set_runtime --------------------------------
    def set_runtime(self, runtime: Runtime) -> None:
        _raw.webui_set_runtime(c_size_t(self._window), c_size_t(runtime.value))




# == Global functions below ===================================================


# -- get_new_window_id --------------------------
def get_new_window_id() -> int:
    return int(_raw.webui_get_new_window_id)

# -- is_high_contrast ---------------------------
def is_high_contrast() -> bool:
    """Return True if the OS is using a high-contrast theme."""
    return bool(_raw.webui_is_high_contrast())

# -- browser_exist ------------------------------
def browser_exist(browser: Browser) -> bool:
    return bool(_raw.webui_browser_exist(c_size_t(browser.value)))

# -- wait ---------------------------------------
def wait() -> None:
    """Wait until all opened windows get closed."""
    _raw.webui_wait()

# -- exit ---------------------------------------
def exit() -> None:
    """Close all open windows and break out of webui_wait()."""
    _raw.webui_exit()

# -- set_default_root_folder --------------------
def set_default_root_folder(path: str) -> bool:
    return bool(_raw.webui_set_default_root_folder(path.encode("utf-8")))

# -- set_timeout --------------------------------
def set_timeout(seconds: int) -> None:
    _raw.webui_set_timeout(c_size_t(seconds))

# -- encode -------------------------------------
def ui_encode(string: str) -> str:
    return _raw.webui_encode(string.encode("utf-8")).decode("utf-8")

# -- decode -------------------------------------
def ui_decode(string: str) -> str:
    return _raw.webui_decode(string.encode("utf-8")).decode("utf-8")

# -- free ---------------------------------------
def free(ptr: Optional[c_void_p]) -> None:
    if ptr is None:
        raise ValueError("Invalid pointer: Cannot free a null pointer.")
    _raw.webui_free(ptr)

# -- malloc -------------------------------------
def malloc(size: int) -> Optional[int]:
    if size <= 0:
        raise ValueError("Size must be a positive integer.")
    ptr = _raw.webui_malloc(c_size_t(size))
    if not ptr:
        return None  # Allocation failed
    return int(ptr)

# -- open_url -----------------------------------
def open_url(url: str) -> None:
    _raw.webui_open_url(c_char_p(url.encode("utf-8")))

# -- clean --------------------------------------
def clean() -> None:
    _raw.webui_clean()

# -- delete_all_profiles ------------------------
def delete_all_profiles() -> None:
    _raw.webui_delete_all_profiles()

# -- get_free_port ------------------------------
def get_free_port() -> int:
    return int(_raw.webui_get_free_port())

# -- set_config ---------------------------------
def set_config(option: Config, status: bool) -> None:
    _raw.webui_set_config(c_int(option.value), c_bool(status))

# -- get_mime_type ------------------------------
def get_mime_type(file: str) -> str:
    return str(_raw.webui_get_mime_type(c_char_p(file.encode("utf-8"))).decode("utf-8"))


# == SSL/TLS ==================================================================


# -- set_tls_certificate ------------------------
def set_tls_certificate(certificate_pem: str, private_key_pem: str) -> bool:
    return bool(_raw.webui_set_tls_certificate(c_char_p(certificate_pem.encode("utf-8")), c_char_p(private_key_pem.encode("utf-8"))))
