from webui import webui

def close(e: webui.event):
    print("Exit.")
    # Close all opened windows
    webui.exit()

def main():
    # Create new window
    window = webui.window()

    # Bind HTML element IDs with Python functions
    window.bind("__close-btn", close)

    # Show the window
    window.set_root_folder("ui/")

    # Show the window
    window.show("index.html")

    # Wait until all windows get closed
    webui.wait()

if __name__ == "__main__":
	main()
