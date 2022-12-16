from flask import request, Blueprint
from createapp import get_app
import re
from user.models import User, UserProfile
from user.models import db
import bcrypt
from bcrypt import checkpw
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity,jwt_required
from flask_jwt_extended import JWTManager
user = Blueprint('user', __name__)
app = get_app()
jwt = JWTManager(app)


@user.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        email_id = data['email_id']
        username = data['username']
        password = data['password']
        if not email_id:
            return {"data" :{"error": "email cannot be empty"}}, 400
        if not username:
            return {"data" :{"error": "username cannot be empty"}}, 400
        if not password:
            return {"data":{"error": "password cannot be empty"}}, 400
        if not check_email(email_id) :
            return {"data" :{"error": "Please provide a valid email"}}, 400
        if not check_username(username):
            return {"data" :{"error": "Please provide a valid username"}}, 400
        if not password_check(password):
            return {"data" :{"error": "Password should contain least 1 number, 1 special symbol, 1 uppercase letter and 1 lowercase letter and maximum length is 20 and minimum length is 8"}}, 400
        if User.query.filter_by(username=username).first() is not None:
            return {"data":{"error": "Username already exists"}}, 409
        if User.query.filter_by(email=email_id).first() is not None:
            return {"data":{"error": "email already exists"}}, 409

        user_1 = User(username=username, email=email_id, hashed_password=hashing_password(password), is_admin=False)
        profile_1 = UserProfile(None, None, None, None, user_id=user_1.id)

        db.session.add(user_1)
        db.session.commit()
        db.session.add(profile_1)
        db.session.commit()
        return {"data": {"message": "user created"}}, 200
    except KeyError:
        return {"data": {"error" : "provide all signup keys"}}



def hashing_password(password):
    password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    hashed = hashed.decode('utf-8')
    return hashed


def checking_2password(h_password, password):
    hash_password = h_password.encode('utf-8')
    return checkpw(password.encode('utf-8'), hash_password)


def check_email(email):
    mail_id = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.fullmatch(mail_id, email):
        return True
    else:
        return False


def password_check(passwd):
    special_sym = ['$', '@', '#', '%']
    val = True

    if len(passwd) < 6:
        val = False
    if len(passwd) > 20:
        val = False
    if not any(char.isdigit() for char in passwd):
        val = False
    if not any(char.isupper() for char in passwd):
        val = False
    if not any(char.islower() for char in passwd):
        val = False
    if not any(char in special_sym for char in passwd):
        val = False
    if val:
        return val


def check_username(username):
    user_name = "^[A-Za-z][A-Za-z0-9_]{7,29}$"
    if re.fullmatch(user_name, username):
        return True
    else:
        return False


@user.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']

        user_in = User.query.filter_by(username=username).first()

        if user_in is None:
            return {"data": {"error": "username does not exist"}}, 400
        if password == "":
            return {"data": {"error": "provide password"}}, 400
        if user_in and not checking_2password(user_in.hashed_password, password):
            return {"data": {"message": "incorrect password"}}, 409

        if user_in and checking_2password(user_in.hashed_password, password):
            access_token = create_access_token(identity=user_in.id, fresh=True)
            refresh_token = create_refresh_token(identity=user_in.id)
            return {"data":
                {"message": "login successful"},
                 "tokens":{"access_token": access_token,
                    "refresh_token": refresh_token

                }
                    }, 200
    except KeyError:
        return {"data": {"error": "provide all login keys"}}, 400



@user.route('/refresh', methods=["GET"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return {"data": {"access_token": access_token}}

@user.route("/reset_password", methods=["PUT"])
@jwt_required()
def reset_password():
    user_id = get_jwt_identity()
    user_a = User.query.filter_by(id=user_id).first()
    try:
        data = request.get_json()
        current_password = data['current_password']
        new_password = data['new_password']

        if not current_password:
            return {'data':{'error': "please provide current password"}}
        if not new_password:
            return {'data':{'error': "please provide new password"}}
        if not checking_2password(user_a.hashed_password, current_password):
            return {"data": {"error" :"incorrect password"}}, 400
        if not password_check(new_password):
            return {"data": {"error": "current password should contain least 1 uppercase, 1 lowercase, 1 number, and 1 special character and maximum length is 20 and minimum length is 8"}}, 400
        if current_password==new_password:
            return {"data": {"error": "new password should not be same as previous password"}}, 400
        else:
            user_a.hashed_password=hashing_password(new_password)
            db.session.add(user_a)
            db.session.commit()
            return {"data": {"message": "password changed successfully"}}, 200
    except KeyError:
        return {"data": {"error": "key not found"}}, 400





































