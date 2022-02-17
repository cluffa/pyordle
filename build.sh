# need wine32 with python 3.8 installed

wine pip install -r requirements.txt
wine pyinstaller --onefile --add-data 'C:\users\%USERNAME%\Local Settings\Application Data\Programs\Python\Python38-32\Lib\site-packages\pyfiglet;./pyfiglet' pyordle.py

if [ -n "$1" ]; then
  mv dist/pyordle.exe "dist/pyordle_v$1.exe"
else
  mv dist/pyordle.exe dist/pyordle_v0.exe
fi
