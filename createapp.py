from flask import Flask
import os

from datetime import timedelta
app = None


def get_app():
    global app
    if not app:
        app = Flask(__name__)
        app.config['DEBUG'] = False
        app.config['SECRET KEY'] = 'seconds'
        app.config['SQLALCHEMY_ECHO'] = False
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['UPLOAD_FOLDER'] = 'static/catagory'
        app.config['UPLOADED_ITEMS_DEST'] = '/home/qbuser/PycharmProjects/SecondsBackend'
        app.config["JWT_SECRET_KEY"] = "super!@#$$secret"
        app.config['UPLOAD_AD_PICTURE'] = 'static/images_ad'
        app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
        app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/seconds'
    return app
