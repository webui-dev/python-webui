@echo off

echo.
echo * Build React project...

cd webui-react-example
call npm install
call npm run build
cd ..

echo.
echo * Running main.py

python main.py