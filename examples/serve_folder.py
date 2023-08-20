


# Install WebUI
# pip install --upgrade webui2

from webui import webui

def switch_to_second_page(e : webui.event):
	# This function get called when the user
	# click on "SwitchToSecondPage" button
	e.window.show("second.html")

def close_the_application(e : webui.event):
	webui.exit()

def main():

	# Create a window object
	MyWindow = webui.window()

	# Bind am HTML element ID with a python function
	MyWindow.bind('SwitchToSecondPage', switch_to_second_page)
	MyWindow.bind('Exit', close_the_application)

	# Note
	# Add this script to all your .html files:
	# <script src="webui.js"></script>

	# Show a window using the local file
	MyWindow.show("serve_folder.html", webui.browser.chrome)

	# Wait until all windows are closed
	webui.wait()

	print('Thank you.')

if __name__ == "__main__":
	main()
