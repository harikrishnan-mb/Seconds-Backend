from flask import jsonify, request, Blueprint
import re
from user.models import User, UserProfile
from advertisement.models import Advertisement, AdImage, AdPlan, ReportAd, FavouriteAd, Category
from user.models import db
import bcrypt
user = Blueprint('user', __name__)


@user.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email_id = data['email_id']
    username = data['username']
    password = data['password']

    if not email_id:
        return {"message": "email cannot be empty"}, 400
    if not username:
        return {"message": "username cannot be empty"}, 400
    if not check_email(email_id):
        return {"message": "Please provide a valid email"}, 400
    if not check_username(username):
        return {"message": "Please provide a valid username"}, 400
    if User.query.filter_by(username=username).first() is not None:
        return {"message": "Username already exists"}, 403
    if User.query.filter_by(email=email_id).first() is not None:
        return {"message": "email already exists"}, 403

    user_1 = User(username=username, email=email_id, hashed_password=hashing_password(password))
    profile_1 = UserProfile(None, None, None, None, user_id=user_1.id)

    db.session.add(user_1)
    db.session.commit()
    db.session.add(profile_1)
    db.session.commit()
    return {"message": "user created"}


def hashing_password(password):
    password = password.encode('utf-8' )
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return hashed


def check_email(email):
    mail_id = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.fullmatch(mail_id, email):
        return True
    else:
        return False


def check_username(username):
    user_name = "^[A-Za-z][A-Za-z0-9_]{7,29}$"
    if re.fullmatch(user_name, username):
        return True
    else:
        return False
