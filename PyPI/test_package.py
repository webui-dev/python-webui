# This script is for debugging & the development of the WebUI Python wrapper.
# The wrapper source code is located at 'webui/examples/Python/PyPI/Package/src/webui/webui.py'

# [!] Make sure to remove the WebUI package
# pip uninstall webui2

# Import the WebUI local module
import sys
sys.path.append('./Package/src/webui')

import webui

# Use the local WebUI Dynamic lib
# webui.set_library_path('')

# HTML
html = """
<!DOCTYPE html>
<html>
	<head>
		<title>WebUI 2 - Python Wrapper Test</title>
		<script src="webui.js"></script>
		<style>
            body {
                font-family: 'Arial', sans-serif;
                color: white;
                background: linear-gradient(to right, #507d91, #1c596f, #022737);
                text-align: center;
                font-size: 18px;
            }
            button, input {
                padding: 10px; 
                border-radius: 3px; 
                border: 1px solid #ccc; 
                box-shadow: 0 3px 5px rgba(0,0,0,0.1); 
                transition: 0.2s; 
            }
            button {
                background: #3498db; 
                color: #fff; 
                cursor: pointer;
                font-size: 16px;
            }
            h1 { text-shadow: -7px 10px 7px rgb(67 57 57 / 76%); }
            button:hover { background: #c9913d; }
            input:focus { outline: none; border-color: #3498db; }
		</style>
	</head>
	<body>
		<h2>Python Wrapper Test</h2>
		<br>
		<input type="text" id="MyInput" OnKeyUp="document.getElementById('err').innerHTML='&nbsp;';" autocomplete="off" value=\"2\">
		<br>
		<h3 id="err" style="color: #dbdd52">&nbsp;</h3>
		<br>
		<button id="P2JS">Test Python-To-JS</button>
		<button OnClick="MyJS();">Test JS-To-Python</button>
		<button id="Exit">Exit</button>
		<script>
			function MyJS() {
				const number = document.getElementById('MyInput').value;
				JS2P(number).then((response) => {
					document.getElementById('MyInput').value = response;
				});
			}
		</script>
    </body></html>
"""

def all_events(e : webui.event):
	print('Function: all_events()')
	print('Element: ' + e.element)
	print('Type: ' + str(e.event_type))
	print(' ')

def python_to_js(e : webui.event):
	print('Function: python_to_js()')
	print('Element: ' + e.element)
	print('Type: ' + str(e.event_type))
	print('Data: ' + e.window.get_str(e))
	print(' ')
	# Run JavaScript to get the password
	res = e.window.script("return document.getElementById('MyInput').value;")
	# Check for any error
	if res.error is True:
		print("JavaScript Error: [" + res.data + "]")
	else:
		print("JavaScript OK: [" + res.data + "]")
	# Quick JavaScript (no response waiting)
	# e.window.run("alert('Fast!')")
	print(' ')

def js_to_python(e : webui.event):
	print('Function: js_to_python()')
	print('Element: ' + e.element)
	print('Type: ' + str(e.event_type))
	print('Data: ' + e.window.get_str(e, 0))
	print(' ')
	v = int(e.window.get_str(e, 0))
	v = v * 2
	return v

def exit(e : webui.event):
	print('Function: exit()')
	print('Element: ' + e.element)
	print('Type: ' + str(e.event_type))
	print('Data: ' + e.window.get_str(e, 0))
	print(' ')
	webui.exit()

def main():

	# Create a window object
	MyWindow = webui.window()

	# Bind am HTML element ID with a python function
	MyWindow.bind('', all_events)
	MyWindow.bind('P2JS', python_to_js)
	MyWindow.bind('JS2P', js_to_python)
	MyWindow.bind('Exit', exit)

	# Show the window
	MyWindow.show(html, webui.browser.any)

	# Wait until all windows are closed
	webui.wait()

	print('Test Done.')

if __name__ == "__main__":
	main()
