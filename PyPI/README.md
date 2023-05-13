# WebUI PyPI Package

```sh
git clone https://github.com/webui-dev/python-webui.git
cd python-webui/PyPI
python -m pip install --upgrade pip
python -m pip install --upgrade build
python -m pip install --upgrade twine
python -m build
python -m twine upload --repository pypi dist/*
```

```sh
pip install --upgrade webui2
```
