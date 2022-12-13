from flask import Flask
import os

from datetime import timedelta
app = None


def get_app():
    global app
    if not app:
        app = Flask(__name__)
        app.config['DEBUG'] = False
        app.config["JWT_SECRET_KEY"] = "super!@#$$secret"
        app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
        app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/seconds'
    return app
