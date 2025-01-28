import sys
sys.path.append('../../PyPI/Package/src/webui')
import webui

# Install WebUI
# pip install --upgrade webui2
# from webui import webui
import subprocess
import time

class CommandExecutor:
    def __init__(self):
        self.shell = subprocess.Popen(
            ["bash"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

    def execute(self, command):
        sentinel = "_SHELL_END_OF_COMMAND_OUTPUT_"
        self.shell.stdin.write(f"{command}; echo {sentinel}\n")
        self.shell.stdin.flush()
        output : str = ""
        while True:
            line = self.shell.stdout.readline().strip()
            if sentinel in line:
                break
            output = output + line + "\n"
        result = str(output).strip()
        result = result.replace('\r\n', '\n') # Byte
        result = result.replace('\\r\\n', '\\n') # Character
        return result + "\n"

    def close(self):
        self.shell.stdin.close()
        self.shell.terminate()
        self.shell.wait()

def run_command(e : webui.Event):
    cmd = e.get_string_at(0)
    if cmd == "exit":
        webui.exit()
    try:
        command_result = executor.execute(cmd)
        e.return_string(command_result)
    except FileNotFoundError:
        print(f"Command not found '{cmd}'")

executor = CommandExecutor()
MyWindow = webui.Window()
MyWindow.bind("Run", run_command)
MyWindow.set_root_folder("ui/")
MyWindow.show_browser('index.html', webui.Browser.Chrome)
webui.wait()
executor.close()
