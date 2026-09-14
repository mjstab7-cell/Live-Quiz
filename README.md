# Live Quiz App (Flask-SocketIO, deploy on Render)

Files:
- app.py            — server + your quiz questions (edit the QUESTIONS list here)
- requirements.txt  — Python packages
- Procfile          — tells Render how to start the app
- templates/present.html — projector page (open on your laptop, cast to screen)
- templates/join.html    — phone page (people open via the QR code)
- static/           — put any question images here, e.g. static/frog.jpg,
                       then set "media_url": "/static/frog.jpg" in app.py

See the setup instructions Claude gave you for how to put this on GitHub
and deploy it on Render.
