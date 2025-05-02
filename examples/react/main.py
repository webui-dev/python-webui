import os
import mimetypes
from typing import Optional
from dataclasses import dataclass
from webui import webui


@dataclass
class VirtualFile:
    path: str
    body: str


virtual_files: list[VirtualFile] = []
# flat list: [dir_key, index_path, dir_key, index_path, ...]
index_files: list[str] = []


def build_vfs(directory: str):
    """
    Scan a directory tree and populate the global virtual file lists.

    Walks through every file under `directory`, reads its contents as raw bytes
    (decoded via Latin-1 to preserve 1:1 byte -> character mapping), and appends
    a `VirtualFile(path, body)` entry to `virtual_files`. Detects any files
    named `index.*`, recording them in `index_files`.

    Args:
        directory: The root directory whose files will be loaded into memory.

    Globals:
        virtual_files: Cleared and then extended with VirtualFile instances
                       for each file found.
        index_files:   Cleared and then populated with flat [dir_key, index_path]
                       pairs corresponding to each directory's index file.
    """
    global virtual_files, index_files
    virtual_files.clear()
    index_files.clear()

    index_map: dict[str,str] = {}

    for root, _, filenames in os.walk(directory):
        rel_dir = os.path.relpath(root, directory).replace('\\','/')
        if rel_dir == '.':
            rel_dir = ''
        
        for fn in filenames:
            full = os.path.join(root, fn)
            vpath = f"/{rel_dir}/{fn}".replace('//','/')

            # read raw bytes
            with open(full, 'rb') as f:
                body = f.read().decode('latin-1')

            virtual_files.append(VirtualFile(path=vpath, body=body))

            if fn.startswith("index."):
                dir_key = f"/{rel_dir}/".replace('//','/')
                if dir_key not in index_map:
                    index_map[dir_key] = vpath

    # flatten map into list
    for dk, ip in index_map.items():
        index_files.extend([dk, ip])


def virtual_file_system(path: str) -> Optional[VirtualFile]:
    """
    Returns the matching VirtualFile or None.
    """
    global virtual_files

    for vf in virtual_files:
        if vf.path == path:
            return vf
    return None


def vfs(path: str) -> Optional[str]:
    """
    Handler function for set_file_handler(),
    Type needed: Callable[[str], Optional[str]]
    - If exact file found, return "200 OK" headers + body.
    - Else, check index_files for a 302 redirect.
    - Else, return None.
    """
    global index_files

    # Try exact file
    vf = virtual_file_system(path)
    if vf is not None:
        length = len(vf.body)  # latin-1 str length == byte length
        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        header = (
            "HTTP/1.1 200 OK\r\n"
            f"Content-Type: {ctype}\r\n"
            f"Content-Length: {length}\r\n"
            "Cache-Control: no-cache\r\n\r\n"
        )
        return header + vf.body

    # Not found; check for index redirect
    redirect_path = path
    if not redirect_path.endswith('/'):
        redirect_path += '/'

    for i in range(0, len(index_files), 2):
        if index_files[i] == redirect_path:
            location = index_files[i+1]
            header = (
                "HTTP/1.1 302 Found\r\n"
                f"Location: {location}\r\n"
                "Cache-Control: no-cache\r\n\r\n"
            )
            return header

    # No match; will default to normal WebUI file system behavior
    return None


def exit_app(e: webui.Event):
    webui.exit()


def main():
    # Create new window
    react_window = webui.Window()
    
    # Set window size
    react_window.set_size(550, 450)
    
    # Set window position
    react_window.set_position(250, 250)
    
    # Allow multi-user connection to WebUI window
    webui.set_config(webui.Config.multi_client, True)
    
    # Disable WebUI's cookies
    webui.set_config(webui.Config.use_cookies, True)
    
    # Bind react HTML element IDs with a python function
    react_window.bind("Exit", exit_app)

    # VFS (Virtual File System) Example
    #
    # 1. Build your list of files

    # 2. Create a function with this type: 
    #        Callable[[str], Optional[str]]
    # 
    # 3. The parameter should be for a file name
    #    and the return string is the header + body.
    #    Ex. 
    #       def my_handler(filename: str) -> Optional[str]:
    #           response_body = "Hello, World!"
    #           response_headers = (
    #               "HTTP/1.1 200 OK\r\n"
    #               "Content-Type: text/plain\r\n"
    #               f"Content-Length: {len(response_body)}\r\n"
    #               "\r\n"
    #           )
    #           return response_headers + response_body
    #
    # 4. pass that function into the set_file_handler(<handler>)
    
    # Build out the vfs and index list
    build_vfs("./webui-react-example/build")

    # Set a custom files handler
    react_window.set_file_handler(vfs)
    
    # Show the React window
    # react_window.show_browser("index.html", webui.Browser.Chrome)
    react_window.show("index.html")
    
    # Wait until all windows get closed
    webui.wait()

    # Free all memory resources (Optional)
    webui.clean()

    print('Thank you.')


if __name__ == "__main__":
	main()
