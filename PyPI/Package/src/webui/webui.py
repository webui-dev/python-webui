# Python WebUI v2.5.0
#
# http://webui.me
# https://github.com/webui-dev/python-webui
#
# Copyright (c) 2020-2025 Hassan Draga.
# Licensed under MIT License.
# All rights reserved.
# Canada.


import os
import platform
import sys
import ctypes
from ctypes import *
import shutil
import subprocess


lib = None
PTR_CHAR = ctypes.POINTER(ctypes.c_char)
PTR_PTR_CHAR = ctypes.POINTER(PTR_CHAR)


# Scripts Runtime
class browser:
    NoBrowser:int = 0 # No web browser
    any:int = 1 # Default recommended web browser
    chrome:int = 2 # Google Chrome
    firefox:int = 3 # Mozilla Firefox
    edge:int = 4 # Microsoft Edge
    safari:int = 5 # Apple Safari
    chromium:int = 6 # The Chromium Project
    opera:int = 7 # Opera Browser
    brave:int = 8 # The Brave Browser
    vivaldi:int = 9 # The Vivaldi Browser
    epic:int = 10 # The Epic Browser
    yandex:int = 11 # The Yandex Browser
    ChromiumBased:int = 12 # 12. Any Chromium based browser


# event
class event:
    window = 0
    event_type = 0
    element = ""
    event_num = 0
    bind_id = 0


# JavaScript
class javascript:
    error = False
    response = ""


# Scripts Runtime
class runtime:
    none = 0
    deno = 1
    nodejs = 2


# Event types
class eventType:
    DISCONNECTED:int = 0 # Window disconnection event
    CONNECTED:int = 1 # Window connection event
    MOUSE_CLICK:int = 2 # Mouse click event
    NAVIGATION:int = 3 # Window navigation event
    CALLBACK:int = 4 # Function call event


# The window class
class window:


    window = 0
    window_id = ""
    c_events = None
    cb_fun_list = {}


    def __init__(self):
        global lib
        try:
            # Load WebUI Dynamic Library
            _load_library()
            # Check library if correctly loaded
            if lib is None:
                print('WebUI Dynamic Library not found.')
                sys.exit(1)
            # Create new window
            webui_wrapper = None
            webui_wrapper = lib.webui_new_window
            webui_wrapper.restype = c_size_t
            self.window = c_size_t(webui_wrapper())
            # Get the window unique ID
            self.window_id = str(self.window)
            # Initializing events() to be used by
            # WebUI library as a callback
            py_fun = ctypes.CFUNCTYPE(
                ctypes.c_void_p, # RESERVED
                ctypes.c_size_t, # window
                ctypes.c_uint, # event type
                ctypes.c_char_p, # element
                ctypes.c_size_t, # event number
                ctypes.c_uint) # Bind ID
            self.c_events = py_fun(self._events)
        except OSError as e:
            print(
                "WebUI Exception: %s" % e)
            sys.exit(1)


    # def __del__(self):
    #     global lib
    #     if self.window is not None and lib is not None:
    #         lib.webui_close(self.window)


    def _events(self, window: ctypes.c_size_t,
               event_type: ctypes.c_uint,
               _element: ctypes.c_char_p,
               event_number: ctypes.c_longlong,
               bind_id: ctypes.c_uint):
        element = _element.decode('utf-8')
        if self.cb_fun_list[bind_id] is None:
            print('WebUI error: Callback is None.')
            return
        # Create event
        e = event()
        e.window = self # e.window should refer to this class
        e.event_type = int(event_type)
        e.element = element
        e.event_num = event_number
        e.bind_id = bind_id
        # User callback
        cb_result = self.cb_fun_list[bind_id](e)
        if cb_result is not None:
            cb_result_str = str(cb_result)
            cb_result_encode = cb_result_str.encode('utf-8')
            # Set the response
            lib.webui_interface_set_response(window, event_number, cb_result_encode)


    def bind(self, element, func):
        """Bind a specific HTML element click event with a function.
        
        Args:
            element: The HTML element / JavaScript object. Empty element means all events.
            func: The callback function to be called when the event occurs.
            
        Returns:
            The unique bind ID for this event binding.
        """
        global lib
        if self.window == 0:
            _err_window_is_none('bind')
            return
        if lib is None:
            _err_library_not_found('bind')
            return
        # Bind
        bindId = lib.webui_interface_bind(
            self.window,
            element.encode('utf-8'),
            self.c_events)
        # Add CB to the list
        self.cb_fun_list[bindId] = func


    def show(self, content="<html></html>", browser:int=browser.ChromiumBased):
        """Show a window using embedded HTML, or a file.
        
        If the window is already opened then it will be refreshed.
        This will refresh all windows in multi-client mode.
        
        Args:
            content: The HTML content, URL, or a local file path
            browser: The web browser to be used (default: ChromiumBased)
            
        Returns:
            True if showing the window succeeded.
        """
        global lib
        if self.window == 0:
            _err_window_is_none('show')
            return
        if lib is None:
            _err_library_not_found('show')
            return
        # Show the window
        lib.webui_show_browser(self.window, content.encode('utf-8'), ctypes.c_uint(browser))


    def set_runtime(self, rt=runtime.deno):
        """Choose between Deno and Nodejs runtime for .js and .ts files.
        
        Args:
            rt: The runtime to use (deno, nodejs, or none)
        """
        global lib
        if self.window == 0:
            _err_window_is_none('set_runtime')
            return
        if lib is None:
            _err_library_not_found('set_runtime')
            return
        lib.webui_set_runtime(self.window, 
                        ctypes.c_uint(rt))


    def close(self):
        """Close the window.
        
        The window object will still exist but the window will be closed.
        """
        global lib
        if lib is None:
            _err_library_not_found('close')
            return
        lib.webui_close(self.window)


    def is_shown(self):
        """Check if the window is still running.
        
        Returns:
            bool: True if window is running, False otherwise.
        """
        global lib
        if lib is None:
            _err_library_not_found('is_shown')
            return
        r = bool(lib.webui_is_shown(self.window))
        return r


    def get_url(self) -> str:
        """Get current URL of a running window.
        
        Returns:
            str: The full URL string of the window.
        """
        global lib
        if lib is None:
            _err_library_not_found('get_url')
            return
        c_res = lib.webui_get_url
        c_res.restype = ctypes.c_char_p
        data = c_res(self.window)
        decode = data.decode('utf-8')
        return decode


    def get_str(self, e: event, index: c_size_t = 0) -> str:
        """Get an argument as string at a specific index.
        
        Args:
            e: The event struct containing the arguments
            index: The argument position starting from 0
            
        Returns:
            str: The argument value as string.
        """
        global lib
        if lib is None:
            _err_library_not_found('get_str')
            return
        c_res = lib.webui_interface_get_string_at
        c_res.restype = ctypes.c_char_p
        data = c_res(self.window,
                    ctypes.c_uint(e.event_num),
                    ctypes.c_uint(index))
        decode = data.decode('utf-8')
        return decode


    def get_int(self, e: event, index: c_size_t = 0) -> int:
        """Get an argument as integer at a specific index.
        
        Args:
            e: The event struct containing the arguments
            index: The argument position starting from 0
            
        Returns:
            int: The argument value as integer.
        """
        global lib
        if lib is None:
            _err_library_not_found('get_str')
            return
        c_res = lib.webui_interface_get_int_at
        c_res.restype = ctypes.c_longlong
        data = c_res(self.window,
                    ctypes.c_uint(e.event_num),
                    ctypes.c_uint(index))
        return data
    

    def get_bool(self, e: event, index: c_size_t = 0) -> bool:
        """Get an argument as boolean at a specific index.
        
        Args:
            e: The event struct containing the arguments
            index: The argument position starting from 0
            
        Returns:
            bool: The argument value as boolean.
        """
        global lib
        if lib is None:
            _err_library_not_found('get_str')
            return
        c_res = lib.webui_interface_get_bool_at
        c_res.restype = ctypes.c_bool
        data = c_res(self.window,
                    ctypes.c_uint(e.event_num),
                    ctypes.c_uint(index))
        return data
    

    def script(self, script, timeout=0, response_size=(1024 * 8)) -> javascript:
        """Run JavaScript and get the response back.
        
        Args:
            script: The JavaScript code to be executed
            timeout: The execution timeout in seconds (0 means no timeout)
            response_size: The size of response buffer (default: 8KB)
            
        Returns:
            javascript: Object containing response data and error status.
            
        Note:
            Make sure your local buffer can hold the response.
        """
        global lib
        if self.window == 0:
            _err_window_is_none('script')
            return
        if lib is None:
            _err_library_not_found('script')
            return
        # Create Buffer
        buffer = ctypes.create_string_buffer(response_size)
        buffer.value = b""
        # Create a pointer to the buffer
        buffer_ptr = ctypes.pointer(buffer)
        # Run JavaScript
        status = bool(lib.webui_script(self.window, 
            ctypes.c_char_p(script.encode('utf-8')), 
            ctypes.c_uint(timeout), buffer_ptr,
            ctypes.c_uint(response_size)))
        # Initializing Result
        res = javascript()
        res.data = buffer.value.decode('utf-8')
        res.error = not status
        return res


    def run(self, script):
        """Run JavaScript quickly with no waiting for the response.
        
        Args:
            script: The JavaScript code to be executed
        """
        global lib
        if self.window == 0:
            _err_window_is_none('run')
            return
        if lib is None:
            _err_library_not_found('run')
            return
        # Run JavaScript
        lib.webui_run(self.window, 
            ctypes.c_char_p(script.encode('utf-8')))


    def set_root_folder(self, path):
        """Set the web-server root folder path for a specific window.
        
        Args:
            path: The local folder full path to be used as root
        """
        global lib
        if self.window == 0:
            _err_window_is_none('set_root_folder')
            return
        if lib is None:
            _err_library_not_found('set_root_folder')
            return
        # Set path
        lib.webui_set_root_folder(self.window, 
            ctypes.c_char_p(path.encode('utf-8')))


    def set_public(self, status = True):
        """Allow a specific window address to be accessible from a public network.
        
        Args:
            status: True to make window public, False for private (default: True)
        """
        global lib
        if self.window == 0:
            _err_window_is_none('set_public')
            return
        if lib is None:
            _err_library_not_found('set_public')
            return
        # Set public
        lib.webui_set_public(self.window, 
            ctypes.c_bool(status))


    def set_kiosk(self, status: bool):
        """Set the window in Kiosk mode (Full screen).
        
        Args:
            status: True to enable kiosk mode, False to disable
        """
        if self.window == 0:
            _err_window_is_none('set_kiosk')
            return
        lib.webui_set_kiosk(self.window, ctypes.c_bool(status))


    def destroy(self):
        """Close the window and free all memory resources."""
        if self.window == 0:
            _err_window_is_none('destroy')
            return
        lib.webui_destroy(self.window)


    def set_icon(self, icon_path, icon_type):
        """Set the default embedded HTML favicon.
        
        Args:
            icon_path: The icon file path or content
            icon_type: The icon type (e.g., 'image/svg+xml')
        """
        if self.window == 0:
            _err_window_is_none('set_icon')
            return
        lib.webui_set_icon(self.window, ctypes.c_char_p(icon_path.encode('utf-8')), ctypes.c_char_p(icon_type.encode('utf-8')))


    def set_hide(self, status: bool):
        """Set a window in hidden mode.
        
        Args:
            status: True to hide window, False to show
            
        Note:
            Should be called before show().
        """
        if self.window == 0:
            _err_window_is_none('set_hide')
            return
        lib.webui_set_hide(self.window, ctypes.c_bool(status))


    def set_size(self, width: int, height: int):
        """Set the window size.
        
        Args:
            width: The window width in pixels
            height: The window height in pixels
        """
        if self.window == 0:
            _err_window_is_none('set_size')
            return
        lib.webui_set_size(self.window, ctypes.c_uint(width), ctypes.c_uint(height))


    def set_position(self, x: int, y: int):
        """Set the window position.
        
        Args:
            x: The window X coordinate
            y: The window Y coordinate
        """
        if self.window == 0:
            _err_window_is_none('set_position')
            return
        lib.webui_set_position(self.window, ctypes.c_uint(x), ctypes.c_uint(y))


    def set_profile(self, name, path):
        """Set the web browser profile to use.
        
        Args:
            name: The web browser profile name
            path: The web browser profile full path
            
        Note:
            Empty name and path means default user profile.
        """
        if self.window == 0:
            _err_window_is_none('set_profile')
            return
        lib.webui_set_profile(self.window, ctypes.c_char_p(name.encode('utf-8')), ctypes.c_char_p(path.encode('utf-8')))


    def set_port(self, port: int):
        """Set a custom web-server/websocket network port to be used by WebUI.
        
        Args:
            port: The web-server network port WebUI should use
        """
        if self.window == 0:
            _err_window_is_none('set_port')
            return
        lib.webui_set_port(self.window, ctypes.c_size_t(port))


    def get_parent_process_id(self) -> int:
        """Get the ID of the parent process.
        
        Returns:
            int: The parent process id
        """
        if self.window == 0:
            _err_window_is_none('get_parent_process_id')
            return
        return int(lib.webui_get_parent_process_id(self.window))


    def get_child_process_id(self) -> int:
        """Get the ID of the last child process.
        
        Returns:
            int: The child process id
        """
        if self.window == 0:
            _err_window_is_none('get_child_process_id')
            return
        return int(lib.webui_get_child_process_id(self.window))


    """Create a new webui window object using a specified window number.
    @param window_number The window number (should be > 0, and < WEBUI_MAX_IDS)
    @return Returns the same window number if success."""
    def new_window_id(self, window_number: int) -> int:
        global lib
        if lib is None:
            _err_library_not_found('new_window_id')
            return 0
        return int(lib.webui_new_window_id(ctypes.c_size_t(window_number)))


    """Get a free window number that can be used with `webui_new_window_id()`.
    @return Returns the first available free window number. Starting from 1."""
    def get_new_window_id(self) -> int:
        global lib
        if lib is None:
            _err_library_not_found('get_new_window_id')
            return 0
        return int(lib.webui_get_new_window_id())


    """Get the recommended web browser ID to use. If you are already using one, 
    this function will return the same ID.
    @return Returns a web browser ID."""
    def get_best_browser(self) -> int:
        global lib
        if lib is None:
            _err_library_not_found('get_best_browser')
            return 0
        return int(lib.webui_get_best_browser(self.window))


    """Same as `webui_show()`. But start only the web server and return the URL.
    No window will be shown.
    @param content The HTML, Or a local file
    @return Returns the url of this window server."""
    def start_server(self, content: str) -> str:
        global lib
        if lib is None:
            _err_library_not_found('start_server')
            return ""
        c_res = lib.webui_start_server
        c_res.restype = ctypes.c_char_p
        url = c_res(self.window, content.encode('utf-8'))
        return url.decode('utf-8') if url else ""


    """Show a WebView window using embedded HTML, or a file. If the window is already
    open, it will be refreshed. Note: Win32 need `WebView2Loader.dll`.
    @param content The HTML, URL, Or a local file
    @return Returns True if showing the WebView window is successed."""
    def show_wv(self, content: str) -> bool:
        global lib
        if lib is None:
            _err_library_not_found('show_wv')
            return False
        return bool(lib.webui_show_wv(self.window, content.encode('utf-8')))


    """Add a user-defined web browser's CLI parameters.
    @param params Command line parameters"""
    def set_custom_parameters(self, params: str):
        global lib
        if lib is None:
            _err_library_not_found('set_custom_parameters')
            return
        lib.webui_set_custom_parameters(self.window, params.encode('utf-8'))


    """Set the window with high-contrast support. Useful when you want to 
    build a better high-contrast theme with CSS.
    @param status True or False"""
    def set_high_contrast(self, status: bool):
        global lib
        if lib is None:
            _err_library_not_found('set_high_contrast')
            return
        lib.webui_set_high_contrast(self.window, ctypes.c_bool(status))


    """Set the window minimum size.
    @param width The window width
    @param height The window height"""
    def set_minimum_size(self, width: int, height: int):
        global lib
        if lib is None:
            _err_library_not_found('set_minimum_size')
            return
        lib.webui_set_minimum_size(self.window, ctypes.c_uint(width), ctypes.c_uint(height))


    """Set the web browser proxy server to use. Need to be called before `webui_show()`.
    @param proxy_server The web browser proxy_server"""
    def set_proxy(self, proxy_server: str):
        global lib
        if lib is None:
            _err_library_not_found('set_proxy')
            return
        lib.webui_set_proxy(self.window, proxy_server.encode('utf-8'))


    """Navigate to a specific URL. All clients.
    @param url Full HTTP URL"""
    def navigate(self, url: str):
        global lib
        if lib is None:
            _err_library_not_found('navigate')
            return
        lib.webui_navigate(self.window, url.encode('utf-8'))


def _get_current_folder() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def _get_architecture() -> str:
    arch = platform.machine()
    if arch in ['x86_64', 'AMD64', 'amd64']:
        return 'x64'
    elif arch in ['aarch64', 'ARM64', 'arm64']:
        return 'arm64'
    elif arch in ['arm']:
        return 'arm'
    else:
        return arch


def _get_library_folder_name() -> str:
    arch = _get_architecture()
    if platform.system() == 'Darwin':
        return f'/webui-macos-clang-{arch}/webui-2.dylib'
    elif platform.system() == 'Windows':
        return f'\\webui-windows-msvc-{arch}\\webui-2.dll'
    elif platform.system() == 'Linux':
        return f'/webui-linux-gcc-{arch}/webui-2.so'
    else:
        return ""


def _get_library_path() -> str:
    folderName = _get_library_folder_name()
    return _get_current_folder() + folderName


def run_cmd(command):
    subprocess.run(command, shell=True)


def _download_library():
    script = 'sh bootstrap.sh'
    cd = 'cd '
    if platform.system() == 'Windows':
        script = 'bootstrap.bat'
        cd = 'cd /d '
    # Run: `cd {folder} && bootstrap.sh minimal`
    run_cmd(cd + _get_current_folder() + 
               ' && ' + script + ' minimal')


def _load_library():
    global lib
    if lib is not None:
        return
    libPath = _get_library_path()
    if not os.path.exists(libPath):
        _download_library()
    if not os.path.exists(libPath):
        return
    if platform.system() == 'Darwin':
        lib = ctypes.CDLL(libPath)
        if lib is None:
            print(
                "WebUI Dynamic Library not found.")
    elif platform.system() == 'Windows':
        if sys.version_info.major==3 and sys.version_info.minor<=8:
            os.chdir(os.getcwd())
            os.add_dll_directory(os.getcwd())
            lib = ctypes.CDLL(libPath)
        else:
            os.chdir(os.getcwd())
            os.add_dll_directory(os.getcwd())
            lib = cdll.LoadLibrary(libPath)
        if lib is None:
            print("WebUI Dynamic Library not found.")
    elif platform.system() == 'Linux':
        lib = ctypes.CDLL(libPath)
        if lib is None:
            print("WebUI Dynamic Library not found.")
    else:
        print("Unsupported OS")


def exit():
    global lib
    if lib is not None:
        lib.webui_exit()


def free(ptr):
    global lib
    if lib is not None:
        lib.webui_free(ctypes.c_void_p(ptr))


def malloc(size: int) -> int:
    global lib
    if lib is not None:
        return int(lib.webui_malloc(ctypes.c_size_t(size)))


def send_raw(window, function, raw, size):
    global lib
    if lib is not None:
        lib.webui_send_raw(window, ctypes.c_char_p(function.encode('utf-8')), ctypes.c_void_p(raw), ctypes.c_size_t(size))


def clean():
    global lib
    if lib is not None:
        lib.webui_clean()


def delete_all_profiles():
    global lib
    if lib is not None:
        lib.webui_delete_all_profiles()


def delete_profile(window):
    global lib
    if lib is not None:
        lib.webui_delete_profile(ctypes.c_size_t(window))


def set_tls_certificate(certificate_pem, private_key_pem):
    global lib
    if lib is not None:
        lib.webui_set_tls_certificate(ctypes.c_char_p(certificate_pem.encode('utf-8')), ctypes.c_char_p(private_key_pem.encode('utf-8')))


def set_timeout(second):
    global lib
    if lib is None:
        _load_library()
        if lib is None:
            _err_library_not_found('set_timeout')
            return
    lib.webui_set_timeout(ctypes.c_uint(second))


def is_app_running():
    global lib
    if lib is None:
        _load_library()
        if lib is None:
            _err_library_not_found('is_app_running')
            return
    r = bool(lib.webui_interface_is_app_running())
    return r


def wait():
    global lib
    if lib is None:
        _load_library()
        if lib is None:
            _err_library_not_found('wait')
            return
    lib.webui_wait()
    try:
        shutil.rmtree(os.getcwd() + '/__intcache__/')
    except OSError:
        pass


def _err_library_not_found(f):
    print('WebUI ' + f + '(): Library Not Found.')


def _err_window_is_none(f):
    print('WebUI ' + f + '(): window is None.')


"""Get OS high contrast preference.
@return Returns True if OS is using high contrast theme"""
def is_high_contrast() -> bool:
    global lib
    if lib is None:
        _err_library_not_found('is_high_contrast')
        return False
    return bool(lib.webui_is_high_contrast())


"""Check if a web browser is installed.
@return Returns True if the specified browser is available"""
def browser_exist(browser: int) -> bool:
    global lib
    if lib is None:
        _err_library_not_found('browser_exist')
        return False
    return bool(lib.webui_browser_exist(ctypes.c_size_t(browser)))


"""Open an URL in the native default web browser.
@param url The URL to open"""
def open_url(url: str):
    global lib
    if lib is None:
        _err_library_not_found('open_url')
        return
    lib.webui_open_url(url.encode('utf-8'))


"""Get an available usable free network port.
@return Returns a free port"""
def get_free_port() -> int:
    global lib
    if lib is None:
        _err_library_not_found('get_free_port')
        return 0
    return int(lib.webui_get_free_port())


"""Get the HTTP mime type of a file.
@return Returns the HTTP mime string"""
def get_mime_type(file: str) -> str:
    global lib
    if lib is None:
        _err_library_not_found('get_mime_type')
        return ""
    c_res = lib.webui_get_mime_type
    c_res.restype = ctypes.c_char_p
    mime = c_res(file.encode('utf-8'))
    return mime.decode('utf-8') if mime else ""


"""Encode text to Base64. The returned buffer need to be freed.
@param str The string to encode (Should be null terminated)
@return Returns the base64 encoded string"""
def encode(text: str) -> str:
    global lib
    if lib is None:
        _err_library_not_found('encode')
        return ""
    c_res = lib.webui_encode
    c_res.restype = ctypes.c_char_p
    encoded = c_res(text.encode('utf-8'))
    result = encoded.decode('utf-8') if encoded else ""
    free(encoded)
    return result


"""Decode a Base64 encoded text. The returned buffer need to be freed.
@param str The string to decode (Should be null terminated)
@return Returns the base64 decoded string"""
def decode(text: str) -> str:
    global lib
    if lib is None:
        _err_library_not_found('decode')
        return ""
    c_res = lib.webui_decode
    c_res.restype = ctypes.c_char_p
    decoded = c_res(text.encode('utf-8'))
    result = decoded.decode('utf-8') if decoded else ""
    free(decoded)
    return result
