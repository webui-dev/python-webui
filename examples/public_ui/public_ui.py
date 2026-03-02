from webui import webui # GUI
import socket # To get local IP


def get_local_ip():
    # The IP address of the local machine is found by creating a socket connection.
    # The socket connects to an external address, but does not send any data.
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        # Failed, return 'localhost'
        local_ip = 'localhost'
    finally:
        s.close()
    return local_ip

def all_events(e : webui.Event):
	if e.event_type == webui.EventType.CONNECTED:
		print('Connected.')
	if e.event_type == webui.EventType.DISCONNECTED:
		print('Disconnected.')

def exit(e : webui.Event):
	webui.exit()

def main():
    html = """
        <html>
		    <script src="webui.js"></script>
	        Hello! This is a public UI.<br>
			<br>
			<button id="Exit">Exit</button>
		</html>
        """

    # New window
    my_window = webui.Window()

    # Make the window URL accessible from public networks
    my_window.set_public(True)

    # Wait forever (Otherwise WebUI will timeout after 30s)
    webui.set_timeout(0)
	
    # Bind
    my_window.bind('', all_events)
    my_window.bind('Exit', exit)

    # Start the window without any browser
    my_window.show_browser(html, webui.Browser.NoBrowser)

    # Get URL of the window
    url = my_window.get_url()
	
    # Get local IP
    local_ip = get_local_ip()
	
    # Replace `localhost` with IP
    link = url.replace('localhost', local_ip)
	
    # Print
    print(f'The UI link is: {link}')

    # Wait until all windows are closed
    webui.wait()
    print('Thank you.')

if __name__ == "__main__":
	main()
