# Python WebUI v2.4.3

> Use any web browser as GUI, with Python in the backend and HTML5 in the frontend, all in a lightweight Python package.

## Features

- Portable (*Needs only a web browser at runtime*)
- Lightweight (*Few Kb library*) & Small memory footprint
- Fast binary communication protocol
- Multi-platform & Multi-Browser
- Using private profile for safety
- Original library is written in Pure C

## Documentation

* [Online Documentation](https://webui.me/docs/#/python_api)

## Install

```sh
pip install webui2
```

## Example

```python
from webui import webui

MyWindow = webui.window()
MyWindow.show('<html><script src="webui.js"></script> Hello World! </html>')
webui.wait()
```
