echo
echo "* Build React project..."

cd webui-react-example
npm install || exit
npm run build || exit
cd ..

echo
echo "* Running main.py"

python3 main.py