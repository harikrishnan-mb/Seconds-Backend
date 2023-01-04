from flask import request, Blueprint
from createapp import get_app
import re
from user.models import User, UserProfile
from user.models import db
import bcrypt
from bcrypt import checkpw
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity,jwt_required
from flask_jwt_extended import JWTManager
import messages
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
            return {"data" :{"error": "email cannot be empty", "error_id": 1005}}, 400
        if not username:
            return {"data" :{"error": "username cannot be empty", "error_id": 1006}}, 400
        if not password:
            return {"data":{"error": "password cannot be empty", "error_id": 1007}}, 400
        if not check_email(email_id):
            return {"data" :{"error": "please provide a valid email", "error_id": 1008}}, 400
        if not check_username(username):
            return {"data" :{"error": "please provide a valid username", "error_id": 1009}}, 400
        if not password_check(password):
            return {"data" :{"error": "password should contain least 1 number, 1 special symbol, 1 uppercase letter and 1 lowercase letter and maximum length is 20 and minimum length is 8", "error_id": 1010}}, 400
        if user_query(username) is not None:
            return {"data":{"error": "username already exists", "error_id": 1011}}, 409
        if user_mail_query(email_id) is not None:
            return {"data":{"error": "email already exists", "error_id": 1012}}, 409

        return user_profile_commit(username, email_id, password)
    except KeyError:
        return {"data": {"error" : "provide all signup keys","error_id": 1013}}, 400
def user_query(username):
    query=User.query.filter_by(username=username).first()
    return query

def user_mail_query(email_id):
    query=User.query.filter_by(email=email_id).first()
    return query

def user_profile_commit(username, email_id, password):
    user_1 = User(username=username, email=email_id, hashed_password=hashing_password(password), is_admin=False)
    profile_1 = UserProfile(None, None, None, None, user_id=user_1.id)

    db.session.add(user_1)
    db.session.commit()
    db.session.add(profile_1)
    db.session.commit()
    return {"data": {"message": "user created"}}, 200


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

        if user_filter_db(username) is None:
            return {"data": {"error": "username does not exist", "error_id": 1001}}, 400
        if password == "":
            return {"data": {"error": "provide password", "error_id": 1002}}, 400
        if user_filter_db(username) and password_match(username,password):
            return checking_userpassword(username, password)
        return {"data": {"error": "incorrect password", "error_id": 1003}}, 409

    except KeyError:
        return {"data": {"error": "provide all login keys", "error_id": 1004}}, 400

def user_filter_db(username):
    user_in = User.query.filter_by(username=username).first()
    return user_in

def password_match(username,password):
    validate_password=checking_2password(user_filter_db(username).hashed_password, password)
    return validate_password

def checking_userpassword(username, password):
    user_in = User.query.filter_by(username=username).first()
    if user_in and checking_2password(user_in.hashed_password, password):
        access_token = create_access_token(identity=user_in.id, fresh=True)
        refresh_token = create_refresh_token(identity=user_in.id)
        return {"data":
                    {"message": "Login successful"},
                "tokens": {"access_token": access_token,
                           "refresh_token": refresh_token

                           }
                }, 200


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
    # filter_user(user_id)
    try:
        data = request.get_json()
        current_password = data['current_password']
        new_password = data['new_password']

        if not current_password:
            return {'data':{'error': " provide current password", "error_id": 1014}}, 400
        if not new_password:
            return {'data':{'error': "provide new password", "error_id": 1015}}, 400
        if not matching_password(user_id, current_password):
            return {"data": {"error" :"incorrect password", "error_id": 1003}}, 400
        if not password_check(new_password):
            return {"data": {"error": "current password should contain least 1 uppercase, 1 lowercase, 1 number, and 1 special character and maximum length is 20 and minimum length is 8", 'error_id': 1010}}, 400
        if current_password==new_password:
            return {"data": {"error": "new password should not be same as previous password", "error_id": 1017}}, 400

        return reset_password_db(user_id, new_password)
    except KeyError:
        return {"data": {"error": "key not found", "error_id": 1018}}, 400

def filter_user(user_id):
    user_a = User.query.filter_by(id=user_id).first()
    return user_a

def matching_password(user_id,current_password):
    user_a = User.query.filter_by(id=user_id).first()
    user_filter=checking_2password(user_a.hashed_password, current_password)
    return user_filter

def reset_password_db(user_id, new_password):
    user_a = User.query.filter_by(id=user_id).first()
    filter_user(user_id).hashed_password = hashing_password(new_password)
    db.session.add(filter_user(user_id))
    db.session.commit()
    return {"data": {"message": "password changed successfully"}}, 200










































