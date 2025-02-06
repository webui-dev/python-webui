# Install WebUI
# pip install --upgrade webui2
from webui import webui

# CSS
css = """
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
"""

# HTML
login_html = f"""
<!DOCTYPE html>
<html>
	<head>
		<title>WebUI 2 - Python Example</title>
		<script src="webui.js"></script>
		<style>
			{css}
		</style>
	</head>
	<body>
		<h1>WebUI Python Example</h1>
		<br>
		<input type="password" id="MyInput" OnKeyUp="document.getElementById('err').innerHTML='&nbsp;';" autocomplete="off">
		<h3 id="err" style="color: #dbdd52">&nbsp;</h3>
		<br>
		<button id="CheckPassword">Check Password</button> - <button id="Exit">Exit</button>
	</body>
</html>
"""

dashboard_html = f"""
<!DOCTYPE html>
<html>
	<head>
		<title>Dashboard</title>
		<script src="webui.js"></script>
		<style>
			{css}
		</style>
	</head>
	<body>
		<h1>Welcome !</h1>
		<br>
		<br>
	<button id="Exit">Exit</button>
	</body>
</html>
"""

# This function get called every time the user click on "MyButton1"
def check_the_password(e : webui.Event):

	# Run JavaScript to get the password
	res = e.window.script("return document.getElementById(\"MyInput\").value;")

	# Check for any error
	if res.error is True:
		print("JavaScript Error: " + res.data)
		return

	# Check the password
	if res.data == "123456":
		print("Password is correct.")
		e.window.show(dashboard_html)
	else:
		print("Wrong password: " + res.data)
		e.window.script(" document.getElementById('err').innerHTML = '[ ! ] Wrong password'; ")

def close_the_application(e : webui.Event):
	webui.exit()

def main():

	# Create a window object
	my_window = webui.Window()

	# Bind am HTML element ID with a python function
	my_window.bind('CheckPassword', check_the_password)
	my_window.bind('Exit', close_the_application)

	# Show the window
	my_window.show_browser(login_html, webui.Browser.Chrome)

	# Wait until all windows are closed
	webui.wait()

	print('Thank you.')

if __name__ == "__main__":
	main()
