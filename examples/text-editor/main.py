from tkinter import filedialog
from webui import webui

import tkinter as tk
import base64 as b64
  
file_path = ""

def encodeStr(string: str) -> str:
    string_bytes = string.encode("ascii")
    b64_bytes = b64.b64encode(string_bytes)
    b64_string = b64_bytes.decode("ascii")

    return b64_string

def close(e: webui.event):
    print("Exit.")

    # Close all opened windows
    webui.exit()

def openFile(e: webui.event):
    global file_path

    print("Open.")

    # Initialize tkinker
    root = tk.Tk()
    root.withdraw()

    # Open file dialog
    file_path = filedialog.askopenfilename()

    # If no file was chosen, return
    if len(file_path) == 0:
        return
    
    with open(file_path) as file:
        file_content = file.read()  # read file contents into variable
    
    # Send data back to Javascript
    e.window.run(f"addText('{encodeStr(file_content)}')")
    e.window.run(f"SetFile('{encodeStr(file_path)}')")   

def save(e: webui.event):
    print("Save.")

    with open(file_path, "w") as file:
        file.write(e.data) # Write data received from the UI

def main():
    # Create new window
    window = webui.window()

    # Bind HTML element IDs with Python functions
    window.bind("Open", openFile)
    window.bind("Save", save)
    window.bind("Close", close)

    # Show the window
    window.show("ui/MainWindow.html")

    # Wait until all windows get closed
    webui.wait()

if __name__ == "__main__":
	main()
