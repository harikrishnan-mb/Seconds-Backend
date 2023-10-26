from flask import Flask
import os
from dotenv import load_dotenv
from datetime import timedelta
app = None
load_dotenv()


def get_app():
    global app
    if not app:
        app = Flask(__name__)
        app.config['DEBUG'] = True
        app.config['TESTING'] = False
        app.config['SECRET_KEY'] = "secret"
        app.config['SQLALCHEMY_ECHO'] = False
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['UPLOAD_FOLDER'] = 'static/catagory'
        app.config['UPLOADED_ITEMS_DEST'] = os.getcwd()
        app.config['UPLOADED_PROFILE_DEST'] = 'static/profile'
        app.config["JWT_SECRET_KEY"] = os.getenv("JWT")
        app.config['UPLOAD_AD_PICTURE'] = 'static/images_ad'
        app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=1)
        app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE')
        app.config['S3_BUCKET'] = os.getenv('S3_BUCKET_NAME')
        app.config['S3_KEY'] = os.getenv("AWS_ACCESS_KEY")
        app.config['S3_SECRET'] = os.getenv("AWS_ACCESS_SECRET")
        app.config['S3_LOCATION'] = os.getenv('S3_LOCATION')
        app.config['COUNT_OF_REPORTS'] = 2
        app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USERNAME'] = 'seconds.clone@gmail.com'
        app.config['MAIL_PASSWORD'] = 'vzcajvmyaabvmywo'
        app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
        app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
    return app
