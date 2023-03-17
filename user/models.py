from datetime import datetime
from database import get_db

db = get_db()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_password = db.Column(db.Text, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)

    # Relationship
    user_profiles = db.relationship('UserProfile', backref='user', uselist=False)
    report_ads = db.relationship('ReportAd', backref='user')
    favourite_ads = db.relationship('FavouriteAd', backref='user')
    # sender = db.relationship('Message', backref='user')
    # notification = db.relationship('Notification', backref='user')
    # receiver = db.relationship('Message', backref='user')

    def __init__(self, username, email, hashed_password, is_admin):
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.is_admin = is_admin

    def __str__(self):
        return f"User with {self.username} created"


class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.BigInteger, unique=True, nullable=True)
    address = db.Column(db.Text, nullable=True)
    photo = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, phone, address, photo, user_id):
        self.name = name
        self.phone = phone
        self.address = address
        self.photo = photo
        self.user_id = user_id

    def __str__(self):
        return f"Userprofile with {self.name} is updated"
