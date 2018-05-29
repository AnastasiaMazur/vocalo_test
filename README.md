# vocalo_test
1) If you want to use the app properly, you should provide HTTPS connection or install ngrok (https://ngrok.com/).

2) Go to the project folder.

3) Create virtual environment and activate it:
```
virtualenv -p /usr/bin/python3.5 env
source env/bin/activate
```

4) Install requirements:
```
pip install -r requirements.txt
```

5) Change MONGODB_SETTINGS to your DB settings in settings.py.

6) Change REDIRECT_URI to yours in settings.py.

7) Run the app:
```
python app.py
```
