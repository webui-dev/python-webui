## React WebUI Example

This is a basic example of how to use WebUI with React to generate a portable single executable program. WebUI will run the internal web server and use any installed web browser as GUI to show the React UI.

__NOTE: To make an executable for python, look into `pyinstaller` or similar type libraries (pathing may have to be automated in some places to differentiate runtime and built file locations)__

![Screenshot](webui_react.png)

### How to use it?

1. Run script `build_react` to re-build the React project and run the pyhton file

### How to create a React WebUI project from scratch?

1. Run `npx create-react-app my-react-app` to create a React app using NPM
2. Add `<script src="webui.js"></script>` into `public/index.html` to connect UI with the backend
3. Copy or make your own vfs functions similar to how it's done in main.py
4. Build the react-app portion with `npm run build`; This step must be done for every change you make to the react portion of the app
5. Now, run `python main.py` or whatever your main entry script is.

### Other backend languages examples:

- Coming soon...
