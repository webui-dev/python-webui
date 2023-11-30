
# Python WebUI v2.4.3
#
# http://webui.me
# https://github.com/webui-dev/python-webui
#
# Copyright (c) 2020-2023 Hassan Draga.
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


    # Bind a specific html element click event with a function. Empty element means all events.
    def bind(self, element, func):
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


    # Show a window using a embedded HTML, or a file. If the window is already opened then it will be refreshed.
    def show(self, content="<html></html>", browser:int=browser.ChromiumBased):
        global lib
        if self.window == 0:
            _err_window_is_none('show')
            return
        if lib is None:
            _err_library_not_found('show')
            return
        # Show the window
        lib.webui_show_browser(self.window, content.encode('utf-8'), ctypes.c_uint(browser))


    # Chose between Deno and Nodejs runtime for .js and .ts files.
    def set_runtime(self, rt=runtime.deno):
        global lib
        if self.window == 0:
            _err_window_is_none('set_runtime')
            return
        if lib is None:
            _err_library_not_found('set_runtime')
            return
        lib.webui_set_runtime(self.window, 
                        ctypes.c_uint(rt))


    # Close the window.
    def close(self):
        global lib
        if lib is None:
            _err_library_not_found('close')
            return
        lib.webui_close(self.window)


    def is_shown(self):
        global lib
        if lib is None:
            _err_library_not_found('is_shown')
            return
        r = bool(lib.webui_is_shown(self.window))
        return r


    def get_url(self) -> str:
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
    

    # Run a JavaScript, and get the response back (Make sure your local buffer can hold the response).
    def script(self, script, timeout=0, response_size=(1024 * 8)) -> javascript:
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


    # Run JavaScript quickly with no waiting for the response
    def run(self, script):
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


    # Set the web-server root folder path for a specific window
    def set_root_folder(self, path):
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


    # Allow a specific window address to be accessible from a public network
    def set_public(self, status = True):
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
    if platform.system() == 'Windows':
        script = 'bootstrap.bat'
    # Run: `cd {folder} && bootstrap.sh minimal`
    run_cmd('cd ' + _get_current_folder() + 
               ' && ' + script + ' minimal')


# Load WebUI Dynamic Library
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


# Close all opened windows. webui_wait() will break.
def exit():
    global lib
    if lib is not None:
        lib.webui_exit()


# Set startup timeout
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


# Wait until all opened windows get closed.
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


# 
def _err_library_not_found(f):
    print('WebUI ' + f + '(): Library Not Found.')


#
def _err_window_is_none(f):
    print('WebUI ' + f + '(): window is None.')
