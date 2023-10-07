# Install WebUI
# pip install --upgrade webui2

from webui import webui

MyWindow = webui.window()
MyWindow.show('<html><head><script src=\"webui.js\"></script></head> Hello World ! </html>')
webui.wait()
print('Thank you.')
