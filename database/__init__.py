from flask_sqlalchemy import SQLAlchemy
from createapp import get_app


db = None


def get_db():
    global db
    if not db:
        app = get_app()
        db = SQLAlchemy(app)
        with app.app_context():
            db.create_all()
    return db


