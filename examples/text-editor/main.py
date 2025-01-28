import sys
sys.path.append('../../PyPI/Package/src/webui')
import webui

# from webui import webui

def close(e: webui.Event):
    print("Exit.")
    # Close all opened windows
    webui.exit()

def main():
    # Create new window
    window = webui.Window()

    # Bind HTML element IDs with Python functions
    window.bind("__close-btn", close)

    # Show the window
    window.set_root_folder("ui/")

    # Show the window
    window.show_browser("index.html", webui.Browser.Chrome)

    # Wait until all windows get closed
    webui.wait()

if __name__ == "__main__":
	main()
