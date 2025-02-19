from webui import webui

def main():
    # Create an instance of a Window object
    my_window = webui.Window()

    # Open an image file and read it in as byte data.
    with open("./webui_python.png", 'rb') as file:
        raw_bytes: bytes = file.read()

    # Open the window using the html file in the project while getting the appropriate browser for the user.
    my_window.show_browser("index.html", my_window.get_best_browser())

    #print(raw_bytes)
    # Send over the byte data from the picture to the javascript function we have in the html.
    my_window.send_raw_to_javascript("myJavaScriptFunc", raw_bytes)

    # waits for all windows to close before terminating the program.
    webui.wait()

if __name__ == "__main__":
    main()


