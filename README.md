# WebUI Python v2.3.0

[![Website](https://img.shields.io/circleci/project/github/badges/shields/master?style=for-the-badge)](https://github.com/webui-dev/python-webui) [![Website](https://img.shields.io/github/issues/webui-dev/python-webui.svg?branch=master&style=for-the-badge&url=https://google.com)](https://github.com/webui-dev/python-webui/issues) [![Website](https://img.shields.io/website?label=webui.me&style=for-the-badge&url=https://google.com)](https://webui.me/)

> Use any web browser as GUI, with Python in the backend and HTML5 in the frontend, all in a lightweight Python pypi package.

![ScreenShot](screenshot.png)

## Features

- Fully Independent (*No need for any third-party runtimes*)
- Lightweight *~900 Kb* for the whole package & Small memory footprint
- Fast binary communication protocol between WebUI and the browser (*Instead of JSON*)
- Multi-platform & Multi-Browser
- Using private profile for safety
- Original library written in Pure C

## Screenshot

This [text editor example](https://github.com/webui-dev/python-webui/tree/main/examples) is written in Python using WebUI as the GUI library.

![ScreenShot](webui_python_example.png)

## Installation

`pip install webui2`

## Minimal Example

```python
from webui import webui

MyWindow = webui.window()
MyWindow.show('<html>Hello World</html>')
webui.wait()
```

[More examples](https://github.com/webui-dev/python-webui/tree/main/examples)

## Documentation

 - [Online Documentation](https://webui.me/docs/#/python_api)

## CppCon 2019 Presentation

[Borislav Stanimirov](https://ibob.bg/) explained at [C++ Conference 2019 (*YouTube*)](https://www.youtube.com/watch?v=bbbcZd4cuxg) how beneficial it is to use the web browser as GUI.

<!-- <div align="center">
  <a href="https://www.youtube.com/watch?v=bbbcZd4cuxg"><img src="https://img.youtube.com/vi/bbbcZd4cuxg/0.jpg" alt="Embrace Modern Technology: Using HTML 5 for GUI in C++ - Borislav Stanimirov - CppCon 2019"></a>
</div> -->

![ScreenShot](cppcon_2019.png)

## UI & The Web Technologies

Web application UI design is not just about how a product looks but how it works. Using web technologies in your UI makes your product modern and professional, And a well-designed web application will help you make a solid first impression on potential customers. Great web application design also assists you in nurturing leads and increasing conversions. In addition, it makes navigating and using your web app easier for your users.

## Why Use Web Browser?

Today's web browsers have everything a modern UI needs. Web browsers are very sophisticated and optimized. Therefore, using it as a GUI will be an excellent choice. While old legacy GUI lib is complex and outdated, a WebView-based app is still an option. However, a WebView needs a huge SDK to build and many dependencies to run, and it can only provide some features like a real web browser. That is why WebUI uses real web browsers to give you full features of comprehensive web technologies while keeping your software lightweight and portable.

## How does it work?

![ScreenShot](webui_diagram.png)

Think of WebUI like a WebView controller, but instead of embedding the WebView controller in your program, which makes the final program big in size, and non-portable as it needs the WebView runtimes. Instead, by using WebUI, you use a tiny static/dynamic library to run any installed web browser and use it as GUI, which makes your program small, fast, and portable. **All it needs is a web browser**.

## Runtime Dependencies Comparison

|  | WebView | Qt | WebUI |
| ------ | ------ | ------ | ------ |
| Runtime Dependencies on Windows | *WebView2* | *QtCore, QtGui, QtWidgets* | ***A Web Browser*** |
| Runtime Dependencies on Linux | *GTK3, WebKitGTK* | *QtCore, QtGui, QtWidgets* | ***A Web Browser*** |
| Runtime Dependencies on macOS | *Cocoa, WebKit* | *QtCore, QtGui, QtWidgets* | ***A Web Browser*** |

## Supported Web Browsers

| OS | Browser | Status |
| ------ | ------ | ------ |
| Windows | Mozilla Firefox | ✔️ |
| Windows | Google Chrome | ✔️ |
| Windows | Microsoft Edge | ✔️ |
| Windows | Chromium | ✔️ |
| Windows | Yandex | ✔️ |
| Windows | Brave | ✔️ |
| Windows | Vivaldi | ✔️ |
| Windows | Epic | ✔️ |
| Windows | Opera | *coming soon* |
| - | - | - |
| Linux | Mozilla Firefox | ✔️ |
| Linux | Google Chrome | ✔️ |
| Linux | Microsoft Edge | ✔️ |
| Linux | Chromium | ✔️ |
| Linux | Yandex | ✔️ |
| Linux | Brave | ✔️ |
| Linux | Vivaldi | ✔️ |
| Linux | Epic | *Does Not Exist* |
| Linux | Opera | *coming soon* |
| - | - | - |
| macOS | Mozilla Firefox | ✔️ |
| macOS | Google Chrome | ✔️ |
| macOS | Microsoft Edge | ✔️ |
| macOS | Chromium | ✔️ |
| macOS | Yandex | ✔️ |
| macOS | Brave | ✔️ |
| macOS | Vivaldi | ✔️ |
| macOS | Epic | ✔️ |
| macOS | Apple Safari | *coming soon* |
| macOS | Opera | *coming soon* |

## Supported Languages

| Language | Status | Link |
| ------ | ------ | ------ |
| C/C++ | ✔️ | [WebUI](https://github.com/webui-dev/webui) |
| Python | ✔️ | [Python-WebUI](https://github.com/webui-dev/python-webui) |
| TypeScript / JavaScript | ✔️ | [Deno](https://github.com/webui-dev/deno-webui) |
| Go | ✔️ | [Go-WebUI](https://github.com/webui-dev/go-webui) |
| Rust | *Not Complete* | [Rust-WebUI](https://github.com/webui-dev/rust-webui) |
| V | ✔️ | [V-WebUI](https://github.com/webui-dev/v-webui) |
| Nim | ✔️ | [Nim-WebUI](https://github.com/webui-dev/nim-webui) |
| Zig | *Not Complete* | [Zig-WebUI](https://github.com/webui-dev/zig-webui) |

### License

> Licensed under MIT License.

### Stargazers

[![Stargazers repo roster for @webui-dev/python-webui](https://reporoster.com/stars/webui-dev/python-webui)](https://github.com/webui-dev/python-webui/stargazers)
