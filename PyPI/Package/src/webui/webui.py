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
NoBrowser: No web browser

AnyBrowser: Default recommended web browser

Chrome: Google Chrome

Firefox: Mozilla Firefox

Edge: Microsoft Edge

Safari: Apple Safari

Chromium: The Chromium Project

Opera: Opera Browser

Brave: The Brave Browser

Vivaldi: The Vivaldi Browser

Epic: The Epic Browser

Yandex: The Yandex Browser

ChromiumBased: Any Chromium based browser

Webview: WebView (Non-web-browser)
"""

Runtime     = _raw.WebuiRuntime
"""
NoRuntime: Prevent WebUI from using any runtime for .js and .ts files

Deno: Use Deno runtime for .js and .ts files

NodeJS: Use Nodejs runtime for .js files

Bun: Use Bun runtime for .js and .ts files
"""

EventType   = _raw.WebuiEvent
"""
DISCONNECTED: Window disconnection event

CONNECTED: Window connection event

MOUSE_CLICK: Mouse click event

NAVIGATION: Window navigation event

CALLBACK: Function call event
"""

Config      = _raw.WebuiConfig
"""
show_wait_connection:
    Control if 'webui_show()', 'webui_show_browser()' and
    'webui_show_wv()' should wait for the window to connect
    before returns or not.
    Default: True
    
ui_event_blocking:
    Control if WebUI should block and process the UI events
    one a time in a single thread `True`, or process every
    event in a new non-blocking thread `False`. This updates
    all windows. You can use `webui_set_event_blocking()` for
    a specific single window update.
    Default: False

folder_monitor:
    Automatically refresh the window UI when any file in the
    root folder gets changed.
    Default: False

multi_client:
    Allow multiple clients to connect to the same window,
    This is helpful for web apps (non-desktop software),
    Please see the documentation for more details.
    Default: False
    
use_cookies:
    Allow or prevent WebUI from adding `webui_auth` cookies.
    WebUI uses these cookies to identify clients and block
    unauthorized access to the window content using a URL.
    Please keep this option to `True` if you want only a single
    client to access the window content.
    Default: True
    
asynchronous_response:
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

    Caries most of the client-side functions but also has reference to
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
        Rebuild of the underlying C struct for interacting with the C API.
        For internal use.
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
        """Show a window using embedded HTML, a file, or a URL.

        If the window is already open, it will be refreshed. This function handles a single client.

        Args:
            content (str): The HTML, URL, or path to a local file to display in the client.

        Returns:
            bool: True if the window was successfully displayed, False otherwise.

        Examples:
            e.show_client("<html>...</html>")

            e.show_client("index.html")

            e.show_client("http://example.com")
        """
        return bool(_raw.webui_show_client(byref(self._c_event()), content.encode('utf-8')))

    # -- close_client -------------------------------
    def close_client(self) -> None:
        """Close a specific client.

        Args:
            self: This function uses the event struct internally to identify the client.

        Returns:
            None

        Example:
            e.close_client()
        """
        _raw.webui_close_client(byref(self._c_event()))

    # -- send_raw_client ----------------------------
    def send_raw_client(self, function: str, raw: Optional[int], size: int) -> None:
        """Safely send raw data to the UI for a single client.

        This function sends raw data to a JavaScript function in the UI. The JavaScript function must
        be defined to accept the raw data, such as: `function myFunc(myData) {}`.

        Args:
            function (str): The name of the JavaScript function to receive the raw data, encoded in UTF-8.
            raw (Optional[int]): The pointer to the raw data buffer. Must not be `None`.
            size (int): The size of the raw data buffer in bytes.

        Raises:
            ValueError: If `raw` is `None`.

        Example:
            e.send_raw_client("myJavaScriptFunc", my_buffer, 64)
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
        """Navigate the client to a specific URL.

        This function directs the client to load the specified HTTP URL. It supports a single client.

        Args:
            url (str): The full HTTP URL to navigate to, encoded in UTF-8.

        Returns:
            None

        Example:
            e.navigate_client("http://domain.com")
        """
        _raw.webui_navigate_client(byref(self._c_event()), c_char_p(url.encode("utf-8")))

    # -- run_client ---------------------------------
    def run_client(self, script: str) -> None:
        """Run a JavaScript script on the client without waiting for a response.

        This function executes the specified JavaScript code in the client's environment. It does not wait for a response
        or return any result. It supports a single client.

        Args:
            script (str): The JavaScript code to be executed, encoded in UTF-8.

        Returns:
            None

        Example:
            e.run_client("alert('Hello');")
        """
        _raw.webui_run_client(byref(self._c_event()), c_char_p(script.encode("utf-8")))

    # -- script_client ------------------------------
    def script_client(self, script: str, timeout: int = 0, buffer_size: int = 4096) -> JavaScript:
        """Run a JavaScript script on the client and retrieve the response.

        This function executes the specified JavaScript code in the client's environment and retrieves the response.
        Ensure that the buffer size is sufficient to hold the response data. It supports a single client.

        Args:
            script (str): The JavaScript code to execute, encoded in UTF-8.
            timeout (int, optional): The maximum time in seconds to wait for the script execution. Defaults to 0 (no timeout).
            buffer_size (int, optional): The size of the buffer to store the response. Defaults to 4096.

        Returns:
            JavaScript: An object containing the response data and the error status.
            - `data` (str): The response data from the executed script.
            - `error` (bool): True if an execution error occurred, False otherwise.

        Example:
            result = e.script_client("return 4 + 6;", timeout=2)
            print(result.data)  # Output: "10"
            print(result.error)  # Output: False if successful, True otherwise
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
        """Get the number of arguments in the current event.

        This function retrieves the count of arguments available in the event structure
        associated with this instance.

        Returns:
            int: The number of arguments in the current event.

        Example:
            count = e.get_count()
            print(f"The event has {count} arguments.")
        """
        return int(_raw.webui_get_count(byref(self._c_event())))

    # -- get_int_at ---------------------------------
    def get_int_at(self, index: int) -> int:
        """Get an argument as an integer at a specific index.

        This function retrieves the argument at the given index from the event structure
        associated with this instance and returns it as an integer.

        Args:
            index (int): The position of the argument to retrieve, starting from 0.

        Returns:
            int: The argument at the specified index as an integer.

        Example:
            value = e.get_int_at(0)
            print(f"The integer at index 0 is {value}.")
        """
        return int(_raw.webui_get_int_at(byref(self._c_event()), c_size_t(index)))

    # -- get_int ------------------------------------
    def get_int(self) -> int:
        """Get the first argument as an integer.

        This function retrieves the first argument from the event structure
        associated with this instance and returns it as an integer.

        Returns:
            int: The first argument as an integer.

        Example:
            value = e.get_int()
            print(f"The first argument is {value}.")
        """
        return int(_raw.webui_get_int(byref(self._c_event())))

    # -- get_float_at -------------------------------
    def get_float_at(self, index: int) -> float:
        """Get an argument as a float at a specific index.

        This function retrieves the argument at the given index from the event structure
        associated with this instance and returns it as a float.

        Args:
            index (int): The position of the argument to retrieve, starting from 0.

        Returns:
            float: The argument at the specified index as a float.

        Example:
            value = e.get_float_at(0)
            print(f"The float at index 0 is {value}.")
        """
        return float(_raw.webui_get_float_at(byref(self._c_event()), c_size_t(index)))

    # -- get_float ----------------------------------
    def get_float(self) -> float:
        """Get the first argument as a float.

        This function retrieves the first argument from the event structure
        associated with this instance and returns it as a float.

        Returns:
            float: The first argument as a float.

        Example:
            value = e.get_float()
            print(f"The first argument as a float is {value}.")
        """
        return float(_raw.webui_get_float(byref(self._c_event())))

    # -- get_string_at ------------------------------
    def get_string_at(self, index: int) -> str:
        """Get an argument as a string at a specific index.

        This function retrieves the argument at the given index from the event structure
        associated with this instance and returns it as a UTF-8 string. If the argument is
        null, an empty string is returned.

        Args:
            index (int): The position of the argument to retrieve, starting from 0.

        Returns:
            str: The argument at the specified index as a string. Returns an empty string if
            the argument is null.

        Example:
            value = e.get_string_at(0)
            print(f"The string at index 0 is '{value}'.")
        """
        char_ptr = _raw.webui_get_string_at(byref(self._c_event()), c_size_t(index))
        if char_ptr is None:
            return ""
        return str(char_ptr.decode("utf-8"))

    # -- get_string ---------------------------------
    def get_string(self) -> str:
        """Get the first argument as a string.

        This function retrieves the first argument from the event structure
        associated with this instance and returns it as a UTF-8 string. If the
        argument is null, an empty string is returned.

        Returns:
            str: The first argument as a string. Returns an empty string if the
            argument is null.

        Example:
            value = e.get_string()
            print(f"The first argument as a string is '{value}'.")
        """
        char_ptr = _raw.webui_get_string(byref(self._c_event()))
        if char_ptr is None:
            return ""
        return str(char_ptr.decode("utf-8"))

    # -- get_bool_at --------------------------------
    def get_bool_at(self, index: int) -> bool:
        """Get an argument as a boolean at a specific index.

        This function retrieves the argument at the given index from the event structure
        associated with this instance and returns it as a boolean value.

        Args:
            index (int): The position of the argument to retrieve, starting from 0.

        Returns:
            bool: The argument at the specified index as a boolean.

        Example:
            is_valid = e.get_bool_at(0)
            print(f"The boolean value at index 0 is {is_valid}.")
        """
        return bool(_raw.webui_get_bool_at(byref(self._c_event()), c_size_t(index)))

    # -- get_bool -----------------------------------
    def get_bool(self) -> bool:
        """Get the first argument as a boolean.

        This function retrieves the first argument from the event structure
        associated with this instance and returns it as a boolean value.

        Returns:
            bool: The first argument as a boolean.

        Example:
            is_valid = e.get_bool()
            print(f"The first argument as a boolean is {is_valid}.")
        """
        return bool(_raw.webui_get_bool(byref(self._c_event())))

    # -- get_size_at --------------------------------
    def get_size_at(self, index: int) -> int:
        """Get the size in bytes of an argument at a specific index.

        This function retrieves the size in bytes of the argument at the specified index
        from the event structure associated with this instance.

        Args:
            index (int): The position of the argument to retrieve the size for, starting from 0.

        Returns:
            int: The size of the argument at the specified index in bytes.

        Example:
            arg_size = e.get_size_at(0)
            print(f"The size of the argument at index 0 is {arg_size} bytes.")
        """
        return int(_raw.webui_get_size_at(byref(self._c_event()), c_size_t(index)))

    # -- get_size -----------------------------------
    def get_size(self) -> int:
        """Get the size in bytes of the first argument.

        This function retrieves the size in bytes of the first argument from the event
        structure associated with this instance.

        Returns:
            int: The size of the first argument in bytes.

        Example:
            arg_size = e.get_size()
            print(f"The size of the first argument is {arg_size} bytes.")
        """
        return int(_raw.webui_get_size(byref(self._c_event())))

    # -- return_int ---------------------------------
    def return_int(self, n: int) -> None:
        """Return the response to JavaScript as an integer.

        This function sends an integer response to JavaScript from the event structure
        associated with this instance.

        Args:
            n (int): The integer value to send to JavaScript.

        Returns:
            None

        Example:
            e.return_int(123)
        """
        _raw.webui_return_int(byref(self._c_event()), c_longlong(n))

    # -- return_float -------------------------------
    def return_float(self, f: float) -> None:
        """Return the response to JavaScript as a float.

        This function sends a floating-point response to JavaScript from the event structure
        associated with this instance.

        Args:
            f (float): The floating-point number to send to JavaScript.

        Returns:
            None

        Example:
            e.return_float(123.456)
        """
        _raw.webui_return_float(byref(self._c_event()), c_double(f))

    # -- return_string ------------------------------
    def return_string(self, s: str) -> None:
        """Return the response to JavaScript as a string.

        This function sends a string response to JavaScript from the event structure
        associated with this instance. The string is encoded in UTF-8 before being sent.

        Args:
            s (str): The string to send to JavaScript.

        Returns:
            None

        Example:
            e.return_string("Response...")
        """
        _raw.webui_return_string(byref(self._c_event()), c_char_p(s.encode("utf-8")))

    # -- return_bool --------------------------------
    def return_bool(self, b: bool) -> None:
        """Return the response to JavaScript as a boolean.

        This function sends a boolean response to JavaScript from the event structure
        associated with this instance.

        Args:
            b (bool): The boolean value to send to JavaScript.

        Returns:
            None

        Example:
            e.return_bool(True)
        """
        _raw.webui_return_bool(byref(self._c_event()), c_bool(b))


# -- Window Object ------------------------------
class Window:
    """
    WebUI Window Object

    Has all related functions that need a window reference to execute.
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

        # window id but in string format if needed. (currently not in use, legacy from previous wrapper)
        self._window_id: str = str(self._window)

        # Dispatch function conversion to C bind for binding functions
        callback_function_type = _raw.CFUNCTYPE(None, _raw.POINTER(_raw.WebuiEventT))
        self._dispatcher_cfunc = callback_function_type(self._make_dispatcher())

        # Dict to keep track of bound functions: {bind_id: python_function}
        self._cb_func_list: dict = {}

        #
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
        """Bind an HTML element or JavaScript object to a backend function.

        This function binds a frontend HTML element or JavaScript object to a Python
        callback function, allowing interaction between the frontend and backend.
        If an empty string is passed as the element, the function will be bound to all events.

        Args:
            element (str): The name of the HTML element or JavaScript object to bind.
                An empty string binds to all events.
            func (Callable[[Event], None]): The Python callback function to execute when the event occurs.

        Returns:
            int: A unique bind ID that can be used to manage the binding.

        Example:
            def my_function(event: Event):
                print("Event received:", event)

            bind_id = my_window.bind("myFunction", my_function)
            print(f"Function bound with ID: {bind_id}")
        """
        element_c = element.encode('utf-8') if element else None
        bind_id = _raw.webui_bind(c_size_t(self._window), element_c, self._dispatcher_cfunc)
        self._cb_func_list[bind_id] = func
        return bind_id

    # -- get_best_browser ---------------------------
    def get_best_browser(self) -> Browser:
        """Get the recommended web browser ID to use.

        This function retrieves the recommended web browser ID for the current window.
        If a browser is already in use, it returns the same browser ID.

        Returns:
            Browser: The ID of the recommended web browser.

        Example:
            browser_id = my_window.get_best_browser()
            print(f"Recommended browser ID: {browser_id}")
        """
        return Browser(int(_raw.webui_get_best_browser(c_size_t(self._window))))

    # -- show ---------------------------------------
    def show(self, content: str) -> bool:
        """Show a window using embedded HTML, a file, or a URL.

        This function displays a window with the provided content. The content can be
        raw HTML, a local file path, or a URL. If the window is already open, it will be
        refreshed. In multi-client mode, all windows will be refreshed.

        Args:
            content (str): The HTML content, a file path, or a URL to load in the window.

        Returns:
            bool: True if the window was successfully shown, False otherwise.

        Example:
            success = my_window.show("<html>...</html>")
            success = my_window.show("index.html")
            success = my_window.show("http://example.com")
        """
        return bool(_raw.webui_show(c_size_t(self._window), c_char_p(content.encode("utf-8"))))

    # -- show_browser -------------------------------
    def show_browser(self, content: str, browser: Browser) -> bool:
        """Show a window using embedded HTML or a file in a specific web browser.

        This function displays a window with the provided content using a specified web browser.
        The content can be raw HTML, a local file path, or a URL. If the window is already open,
        it will be refreshed. In multi-client mode, all windows will be refreshed.

        Args:
            content (str): The HTML content, a file path, or a URL to load in the window.
            browser (Browser): The web browser to be used.

        Returns:
            bool: True if the window was successfully shown, False otherwise.

        Example:
            success = my_window.show_browser("<html>...</html>", Browser.Chrome)
            success = my_window.show_browser("index.html", Browser.Firefox)
        """
        return bool(_raw.webui_show_browser(c_size_t(self._window), c_char_p(content.encode("utf-8")), c_size_t(browser.value)))

    # -- start_server -------------------------------
    def start_server(self, content: str) -> str:
        """Start a web server and return the server URL.

        This function starts a web server using the provided content but does not show
        a window. The content can be raw HTML, a local file path, or a URL.

        Args:
            content (str): The HTML content, a file path, or a URL to serve.

        Returns:
            str: The URL of the web server.

        Example:
            url = my_window.start_server("/full/root/path")
            print(f"Server started at: {url}")
        """
        return str(_raw.webui_start_server(c_size_t(self._window), c_char_p(content.encode("utf-8"))).decode("utf-8"))

    # -- show_wv ------------------------------------
    def show_wv(self, content: str) -> bool:
        """Show a WebView window using embedded HTML, a file, or a URL.

        This function displays a WebView window with the provided content. The content
        can be raw HTML, a local file path, or a URL. If the window is already open, it
        will be refreshed.

        Note:
            On Win32 systems, `WebView2Loader.dll` is required for this function to work.

        Args:
            content (str): The HTML content, a file path, or a URL to load in the WebView window.

        Returns:
            bool: True if the WebView window was successfully shown, False otherwise.

        Example:
            success = my_window.show_wv("<html>...</html>")
            success = my_window.show_wv("index.html")
            success = my_window.show_wv("http://example.com")
        """
        return bool(_raw.webui_show_wv(c_size_t(self._window), content.encode("utf-8")))

    # -- set_kiosk ----------------------------------
    def set_kiosk(self, status: bool) -> None:
        """Set the window in Kiosk mode (full screen).

        This function enables or disables Kiosk mode for the specified window.
        Kiosk mode forces the window into full-screen mode without window controls.

        Args:
            status (bool): True to enable Kiosk mode, False to disable it.

        Returns:
            None

        Example:
            my_window.set_kiosk(True)  # Enable Kiosk mode
            my_window.set_kiosk(False) # Disable Kiosk mode
        """
        _raw.webui_set_kiosk(c_size_t(self._window), c_bool(status))

    # -- set_custom_parameters ----------------------
    def set_custom_parameters(self, params: str) -> None:
        """Add user-defined command-line parameters for the web browser.

        This function sets custom command-line parameters for the web browser
        used to display the window.

        Args:
            params (str): The command-line parameters to pass to the web browser.

        Returns:
            None

        Example:
            my_window.set_custom_parameters("--remote-debugging-port=9222")
        """
        _raw.webui_set_custom_parameters(c_size_t(self._window), c_char_p(params.encode("utf-8")))

    # -- set_high_contrast --------------------------
    def set_high_contrast(self, status: bool) -> None:
        """Enable or disable high-contrast mode for the window.

        This function enables or disables high-contrast support for the window.
        It is useful when building a high-contrast theme using CSS to improve
        accessibility.

        Args:
            status (bool): True to enable high-contrast mode, False to disable it.

        Returns:
            None

        Example:
            my_window.set_high_contrast(True)  # Enable high-contrast mode
            my_window.set_high_contrast(False) # Disable high-contrast mode
        """
        _raw.webui_set_high_contrast(c_size_t(self._window), c_bool(status))

    # -- close --------------------------------------
    def close(self) -> None:  # TODO: document
        """Close a specific window.

        This function closes the specified window, but the window object still exists
        and can be reopened if needed. It does not affect other windows or clients.

        Returns:
            None

        Example:
            my_window.close()  # Close the current window.
        """
        _raw.webui_close(c_size_t(self._window))

    # -- destroy ------------------------------------
    def destroy(self) -> None:  # TODO: document
        """
        Close this window and free all memory resources used by it.
        """
        _raw.webui_destroy(c_size_t(self._window))

    # -- set_root_folder ----------------------------
    def set_root_folder(self, path: str) -> bool:  # TODO: document
        return bool(_raw.webui_set_root_folder(c_size_t(self._window), path.encode("utf-8")))

    # -- set_file_handler ---------------------------
    def set_file_handler(self, handler: Callable[[str], bytes]) -> None:  # TODO: document
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

        _raw.webui_set_file_handler(c_size_t(self._window), self._file_handler_cfunc)

    # -- set_file_handler_window --------------------
    # TODO: set_file_handler_window
    def set_file_handler_window(self):
        pass

    # -- is_shown -----------------------------------
    def is_shown(self) -> bool:  # TODO: document
        """Return True if the window is currently shown."""
        return bool(_raw.webui_is_shown(c_size_t(self._window)))

    # -- set_icon -----------------------------------
    def set_icon(self, icon: str, icon_type: str) -> None:  # TODO: document
        _raw.webui_set_icon(c_size_t(self._window), icon.encode("utf-8"), icon_type.encode("utf-8"))

    # -- send_raw -----------------------------------
    def send_raw(self, function: str, raw: Optional[c_void_p], size: int) -> None:  # TODO: document
        if raw is None:
            raise ValueError("Invalid pointer: Cannot send a null pointer.")
        _raw.webui_send_raw(
            c_size_t(self._window),
            c_char_p(function.encode("utf-8")),
            c_void_p(raw),
            c_size_t(size)
        )

    # -- set_hide -----------------------------------
    def set_hide(self, status: bool) -> bool:  # TODO: document
        return bool(_raw.webui_set_hide(c_size_t(self._window), c_bool(status)))

    # -- set_size -----------------------------------
    def set_size(self, width: int, height: int) -> None:   # TODO: document
        _raw.webui_set_size(c_size_t(self._window), c_uint(width), c_uint(height))

    # -- set_minimum_size ---------------------------
    def set_minimum_size(self, width: int, height: int) -> None: # TODO: document
        _raw.webui_set_minimum_size(self._window, c_uint(width), c_uint(height))

    # -- set_position -------------------------------
    def set_position(self, x: int, y: int) -> None:   # TODO: document
        _raw.webui_set_position(c_size_t(self._window), c_uint(x), c_uint(y))

    # -- set_profile --------------------------------
    def set_profile(self, name: str, path: str) -> None:  # TODO: document
        _raw.webui_set_profile(c_size_t(self._window), c_char_p(name.encode("utf-8")), c_char_p(path.encode("utf-8")))

    # -- set_proxy ----------------------------------
    def set_proxy(self, proxy_server: str) -> None:  # TODO: document
        _raw.webui_set_proxy(c_size_t(self._window), c_char_p(proxy_server.encode("utf-8")))

    # -- get_url ------------------------------------
    def get_url(self) -> str:  # TODO: document
        """
        Get the current URL as a string.
        """
        return _raw.webui_get_url(c_size_t(self._window)).decode("utf-8")

    # -- set_public ---------------------------------
    def set_public(self, status: bool) -> None:  # TODO: document
        _raw.webui_set_public(c_size_t(self._window), c_bool(status))

    # -- navigate -----------------------------------
    def navigate(self, url: str) -> None:  # TODO: document
        _raw.webui_navigate(c_size_t(self._window), c_char_p(url.encode("utf-8")))

    # -- delete_profile -----------------------------
    def delete_profile(self) -> None:  # TODO: document
        _raw.webui_delete_profile(c_size_t(self._window))

    # -- get_parent_process_id ----------------------
    def get_parent_process_id(self) -> int:  # TODO: document
        return int(_raw.webui_get_parent_process_id(c_size_t(self._window)))

    # -- get_child_process_id -----------------------
    def get_child_process_id(self) -> int:  # TODO: document
        return int(_raw.webui_get_child_process_id(c_size_t(self._window)))

    # -- get_port -----------------------------------
    def get_port(self) -> int:  # TODO: document
        return int(_raw.webui_get_port(c_size_t(self._window)))

    # -- set_port -----------------------------------
    def set_port(self, port: int) -> bool:  # TODO: document
        return bool(_raw.webui_set_port(c_size_t(self._window), c_size_t(port)))

    # -- set_event_blocking -------------------------
    def set_event_blocking(self, status: bool) -> None:  # TODO: document
        _raw.webui_set_event_blocking(c_size_t(self._window), c_bool(status))

    # -- run ----------------------------------------
    def run(self, script: str) -> None:  # TODO: document
        """
        Run JavaScript in the window without waiting for a return.
        """
        _raw.webui_run(c_size_t(self._window), script.encode("utf-8"))

    # -- script -------------------------------------
    def script(self, script: str, timeout: int = 0, buffer_size: int = 4096) -> JavaScript:  # TODO: document
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
            c_size_t(self._window),
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
    def set_runtime(self, runtime: Runtime) -> None:  # TODO: document
        _raw.webui_set_runtime(c_size_t(self._window), c_size_t(runtime.value))




# == Global functions below ===================================================


# -- get_new_window_id --------------------------
def get_new_window_id() -> int:  # TODO: document
    return int(_raw.webui_get_new_window_id)

# -- is_high_contrast ---------------------------
def is_high_contrast() -> bool:  # TODO: document
    """Return True if the OS is using a high-contrast theme."""
    return bool(_raw.webui_is_high_contrast())

# -- browser_exist ------------------------------
def browser_exist(browser: Browser) -> bool:  # TODO: document
    return bool(_raw.webui_browser_exist(c_size_t(browser.value)))

# -- wait ---------------------------------------
def wait() -> None:  # TODO: document
    """Wait until all opened windows get closed."""
    _raw.webui_wait()

# -- exit ---------------------------------------
def exit() -> None:  # TODO: document
    """Close all open windows and break out of webui_wait()."""
    _raw.webui_exit()

# -- set_default_root_folder --------------------
def set_default_root_folder(path: str) -> bool:  # TODO: document
    return bool(_raw.webui_set_default_root_folder(path.encode("utf-8")))

# -- set_timeout --------------------------------
def set_timeout(seconds: int) -> None:  # TODO: document
    _raw.webui_set_timeout(c_size_t(seconds))

# -- encode -------------------------------------
def ui_encode(string: str) -> str:  # TODO: document
    return _raw.webui_encode(string.encode("utf-8")).decode("utf-8")

# -- decode -------------------------------------
def ui_decode(string: str) -> str:  # TODO: document
    return _raw.webui_decode(string.encode("utf-8")).decode("utf-8")

# -- free ---------------------------------------
def free(ptr: Optional[c_void_p]) -> None:  # TODO: document
    if ptr is None:
        raise ValueError("Invalid pointer: Cannot free a null pointer.")
    _raw.webui_free(ptr)

# -- malloc -------------------------------------
def malloc(size: int) -> Optional[int]:  # TODO: document
    if size <= 0:
        raise ValueError("Size must be a positive integer.")
    ptr = _raw.webui_malloc(c_size_t(size))
    if not ptr:
        return None  # Allocation failed
    return int(ptr)

# -- open_url -----------------------------------
def open_url(url: str) -> None:  # TODO: document
    _raw.webui_open_url(c_char_p(url.encode("utf-8")))

# -- clean --------------------------------------
def clean() -> None:  # TODO: document
    _raw.webui_clean()

# -- delete_all_profiles ------------------------
def delete_all_profiles() -> None:  # TODO: document
    _raw.webui_delete_all_profiles()

# -- get_free_port ------------------------------
def get_free_port() -> int:  # TODO: document
    return int(_raw.webui_get_free_port())

# -- set_config ---------------------------------
def set_config(option: Config, status: bool) -> None:  # TODO: document
    _raw.webui_set_config(c_int(option.value), c_bool(status))

# -- get_mime_type ------------------------------
def get_mime_type(file: str) -> str:   # TODO: document
    return str(_raw.webui_get_mime_type(c_char_p(file.encode("utf-8"))).decode("utf-8"))


# == SSL/TLS ==================================================================


# -- set_tls_certificate ------------------------
def set_tls_certificate(certificate_pem: str, private_key_pem: str) -> bool:  # TODO: document
    return bool(_raw.webui_set_tls_certificate(c_char_p(certificate_pem.encode("utf-8")), c_char_p(private_key_pem.encode("utf-8"))))
