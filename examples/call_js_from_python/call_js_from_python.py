# Call JavaScript from Python Example
# pip install --upgrade webui2
from webui import webui

html = """<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <script src="webui.js"></script>
    <title>Call JavaScript from Python Example</title>
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
        margin: 10px;
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
      button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        box-shadow: none;
        filter: grayscale(30%);
      }
      button:disabled:hover { background: #3498db; }
      input:focus { outline: none; border-color: #3498db; }
    </style>
  </head>
  <body>
    <h1>WebUI - Call JavaScript from Python</h1>
    <br>
    <h1 id="count">0</h1>
    <br>
    <button id="ManualBtn" OnClick="my_function_count();">Manual Count</button>
    <br>
    <button id="MyTest" OnClick="AutoTest();">Auto Count (Every 10ms)</button>
    <br>
    <button id="ExitBtn" OnClick="this.disabled=true; my_function_exit();">Exit</button>
    <script>
      let count = 0;
      let auto_running = false;
      function GetCount() {
        return count;
      }
      function SetCount(number) {
        document.getElementById('count').innerHTML = number;
        count = number;
      }
      function AutoTest() {
        if (auto_running) return;
        auto_running = true;
        document.getElementById('MyTest').disabled = true;
        document.getElementById('ManualBtn').disabled = true;
        setInterval(function(){ my_function_count(); }, 10);
      }
    </script>
  </body>
</html>"""


def my_function_count(e: webui.Event):
    # Call JavaScript to get the current count
    res = e.window.script("return GetCount();")

    if res.error:
        if not e.window.is_shown():
            print("Window closed.")
        else:
            print(f"JavaScript Error: {res.data}")
        return

    # Increment and send back
    count = int(res.data) + 1
    e.window.run(f"SetCount({count});")


def my_function_exit(e: webui.Event):
    webui.exit()


def main():
    # Process UI events one at a time (matches C example's ui_event_blocking)
    webui.set_config(webui.Config.ui_event_blocking, True)

    window = webui.Window()
    window.bind("my_function_count", my_function_count)
    window.bind("my_function_exit", my_function_exit)

    window.show(html)
    webui.wait()


if __name__ == "__main__":
    main()
