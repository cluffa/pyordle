# need wine32 with python 3.8 installed
wine pip install -r requirements.txt
wine pyinstaller --onefile --add-data 'C:\\users\\alex\\Local Settings\\Application Data\\Programs\\Python\\Python38-32\\Lib\\site-packages\\pyfiglet;./pyfiglet' pyordle.py
