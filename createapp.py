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
        app.config['DEBUG'] = False
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_ECHO'] = False
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['UPLOAD_FOLDER'] = 'static/catagory'
        app.config['UPLOADED_ITEMS_DEST'] = '/home/qbuser/PycharmProjects/SecondsBackend'
        app.config['UPLOADED_PROFILE_DEST'] = 'static/profile'
        app.config["JWT_SECRET_KEY"] = os.getenv("JWT")
        app.config['UPLOAD_AD_PICTURE'] = 'static/images_ad'
        app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
        app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
        if os.getenv('ENV')=='dev':
            app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/seconds'
        if os.getenv('ENV')=='prod':
            app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/seconds'
        app.config['S3_BUCKET'] = os.getenv('S3_BUCKET_NAME')
        app.config['S3_KEY'] = os.getenv("AWS_ACCESS_KEY")
        app.config['S3_SECRET'] = os.getenv("AWS_ACCESS_SECRET")
        app.config['S3_LOCATION'] = 'https://seconds-web.s3.ap-northeast-1.amazonaws.com/'
    return app
