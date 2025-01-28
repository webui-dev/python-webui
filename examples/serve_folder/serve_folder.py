import sys
sys.path.append('../../PyPI/Package/src/webui')
import webui

# Install WebUI
# pip install --upgrade webui2
# from webui import webui

def switch_to_second_page(e : webui.Event):
	# This function get called when the user
	# click on "SwitchToSecondPage" button
	e.window.show("second.html")

def close_the_application(e : webui.Event):
	webui.exit()

def main():

	# Create a window object
	my_window = webui.Window()

	# Bind am HTML element ID with a python function
	my_window.bind('SwitchToSecondPage', switch_to_second_page)
	my_window.bind('Exit', close_the_application)

	# Note
	# Add this script to all your .html files:
	# <script src="webui.js"></script>

	# Show a window using the local file
	my_window.show_browser("serve_folder.html", webui.Browser.Chrome)

	# Wait until all windows are closed
	webui.wait()
	webui.clean()

	print('Thank you.')

if __name__ == "__main__":
	main()
