from flask import Flask
import os
app = None


def get_app():
    global app
    if not app:
        app = Flask(__name__)
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/Seconds'
    return app
