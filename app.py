from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import psycopg2

app = Flask(__name__)

app.config.update(

    SECRET_KEY='seconds',
    SQLALCHEMY_DATABASE_URI='postgresql://postgres:root@localhost/Seconds',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db = SQLAlchemy(app)
@app.route('/home')
def home():
    return "Seconds Backend"


if __name__ == '__main__':
    app.run(debug=True)
