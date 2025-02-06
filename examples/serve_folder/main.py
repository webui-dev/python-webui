from __future__ import annotations

# --[ Debugging and Development Test ]-----------
# > pip uninstall webui2
import sys
sys.path.append('../../PyPI/Package/src/webui')
import webui

# Install WebUI
# pip install --upgrade webui2
# from webui import webui
from typing import Optional

my_window = webui.Window(1)
my_second_window = webui.Window(2)


def exit_app(e : webui.Event):
	# Close all opened windows
	webui.exit()


def events(e : webui.Event):
	# This function gets called every time
	# there is an event

	if e.event_type == webui.EventType.CONNECTED:
		print("Connected. \n")
	elif e.event_type == webui.EventType.DISCONNECTED:
		print("Disconnected. \n")
	elif e.event_type == webui.EventType.MOUSE_CLICK:
		print("Click. \n")
	elif e.event_type == webui.EventType.NAVIGATION:
		url = e.get_string()
		print("Starting navigation to: %s \n", url)

		# Because we used `webui_bind(MyWindow, "", events);`
		# WebUI will block all `href` link clicks and sent here instead.
		# We can then control the behaviour of links as needed.
		e.window.navigate(url)


def switch_to_second_page(e : webui.Event):
	# This function gets called every
	# time the user clicks on "SwitchToSecondPage"

	# Switch to `/second.html` in the same opened window.
	e.window.show("second.html")


def show_second_window(e : webui.Event):
	# This function gets called every
	# time the user clicks on "OpenNewWindow"

	# Show a new window, and navigate to `/second.html`
	# if it's already open, then switch in the same window
	my_second_window.show("second.html")


def my_file_handler(filename: str) -> Optional[str]:
	print(f"File: {filename} \n")

	if filename == "/test.txt":
		# Const static file example
		return (
			"HTTP/1.1 200 OK\r\n"
			"Content-Type: text/html\r\n"
			"Content-Length: 99\r\n\r\n"
			"<html>"
			"   This is a static embedded file content example."
			"   <script src=\"webui.js\"></script>"
			"</html>"
		)
	elif filename == "/dynamic.html":
		# Dynamic file example
		my_file_handler.count += 1
		body = (
			"<html>"
            "   This is a dynamic file content example. <br>"
            f"   Count: {my_file_handler.count} <a href=\"dynamic.html\">[Refresh]</a><br>"
            "   <script src=\"webui.js\"></script>"
            "</html>"
		)
		header_and_body = (
			"HTTP/1.1 200 OK\r\n"
			"Content-Type: text/html\r\n"
			f"Content-Length: {len(body)}\r\n\r\n"
			+ body
		)
		return header_and_body

	# Other files:
	# A NULL return will make WebUI
	# looks for the file locally.
	return None

my_file_handler.count: int = 0

def main():
	# windows were made globally already at the top.

	# Bind am HTML element ID with a python function
	my_window.bind("SwitchToSecondPage", switch_to_second_page)
	my_window.bind("OpenNewWindow", show_second_window)
	my_window.bind("Exit", exit_app)
	my_second_window.bind("Exit", exit_app)

	#Bind events
	my_window.bind("", events)
	my_second_window.bind("", events)

	# Set the `.ts` and `.js` runtime
	my_window.set_runtime(webui.Runtime.NodeJS)
	# my_window.set_runtime(webui.Runtime.Bun)
	# my_window.set_runtime(webui.Runtime.Deno)

	# Set a custom files handler
	my_window.set_file_handler(my_file_handler)

	# Set window size
	my_window.set_size(800, 800)

	# Set window position
	my_window.set_position(200, 200)

	# Show a window using the local file
	my_window.show("index.html")

	# Wait until all windows get closed
	webui.wait()

	# Free all memory resources (Optional)
	webui.clean()

	print('Thank you.')

if __name__ == "__main__":
	main()
