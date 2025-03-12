from __future__ import annotations

import subprocess
import os
import platform
import sys
from ctypes import *


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
        return f'/webui-macos-clang-{arch}/libwebui-2.dylib'
    elif platform.system() == 'Windows':
        return f'\\webui-windows-msvc-{arch}\\webui-2.dll'
    elif platform.system() == 'Linux':
        return f'/webui-linux-clang-{arch}/libwebui-2.so'  # return f'/webui-linux-gcc-{arch}/libwebui-2.so'
    else:
        return ""


def _get_library_path() -> str:
    folderName = _get_library_folder_name()
    return _get_current_folder() + folderName


def run_cmd(command):
    subprocess.run(command, shell=True)


def _download_library():
    script = 'bash bootstrap.sh'
    cd = 'cd '
    if platform.system() == 'Windows':
        script = 'bootstrap.bat'
        cd = 'cd /d '
    # Run: `cd {folder} && bootstrap.sh minimal`
    run_cmd(cd + _get_current_folder() +
               ' && ' + script + ' minimal')


# Load WebUI Dynamic Library
def load_library() -> CDLL | None:
    library: CDLL | None = None
    lib_path = _get_library_path()
    if not os.path.exists(lib_path):
        _download_library()

    if not os.path.exists(lib_path):
        return library

    if platform.system() == 'Darwin':
        library = CDLL(lib_path)
        if library is None:
            print("WebUI: Dynamic Library not found.")
    elif platform.system() == 'Windows':
        if sys.version_info.major==3 and sys.version_info.minor<=8:
            os.chdir(os.getcwd())
            os.add_dll_directory(os.getcwd())
            library = CDLL(lib_path)
        else:
            os.chdir(os.getcwd())
            os.add_dll_directory(os.getcwd())
            library = cdll.LoadLibrary(lib_path)
        if library is None:
            print("WebUI: Dynamic Library not found.")
    elif platform.system() == 'Linux':
        library = CDLL(lib_path)
        if library is None:
            print("WebUI: Dynamic Library not found.")
    else:
        print("WebUI: Unsupported OS")

    return library
