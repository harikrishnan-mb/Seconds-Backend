from flask import request, Blueprint
from messages import ErrorCodes
from createapp import get_app
from datetime import datetime, timedelta
import re
from flask_mail import Mail, Message
from .validations import generate_otp
import os
from user.models import User, UserProfile
from user.models import db
import string
import bcrypt
import redis
from s3config import s3
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from bcrypt import checkpw
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required,get_jwt, verify_jwt_in_request
from flask_jwt_extended import JWTManager
from flasgger import Swagger, swag_from
load_dotenv
user = Blueprint('user', __name__)
app = get_app()
mail = Mail(app)
jwt = JWTManager(app)


# @swag_from('swagger/signup.yml')
@user.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        email_id = data['email_id']
        username = data['username']
        password = data['password']
        inactive_users = User.query.filter((User.email == email_id or User.username == username) and (User.is_active == False)).all()
        print(inactive_users)
        for each_user in inactive_users:
            print((each_user.created_at > datetime.now()-timedelta(minutes=5)))
            print(datetime.now())
            if each_user.created_at < datetime.now()-timedelta(minutes=5):
                print("hi")
                db.session.delete(each_user)
                db.session.commit()
        if not email_id:
            return {"data": {"error": ErrorCodes.email_cannot_be_empty.value["msg"], "error_id": ErrorCodes.email_cannot_be_empty.value["code"]}}, 400
        if not username:
            return {"data": {"error": ErrorCodes.username_cannot_be_empty.value["msg"], "error_id": ErrorCodes.username_cannot_be_empty.value["code"]}}, 400
        if not password:
            return {"data": {"error": ErrorCodes.password_cannot_be_empty.value["msg"], "error_id": ErrorCodes.password_cannot_be_empty.value["code"]}}, 400
        if not check_email(email_id):
            return {"data": {"error": ErrorCodes.provide_a_valid_email.value["msg"], "error_id": ErrorCodes.provide_a_valid_email.value["code"]}}, 400
        if not check_username(username):
            return {"data": {"error": ErrorCodes.provide_a_valid_username.value["msg"], "error_id": ErrorCodes.provide_a_valid_username.value["code"]}}, 400
        if not password_check(password):
            return {"data": {"error": ErrorCodes.password_format_not_matching.value["msg"], "error_id": ErrorCodes.password_format_not_matching.value["code"]}}, 400
        if checking_username_exist(username) is not None:
            return {"data": {"error": ErrorCodes.username_already_exists.value["msg"], "error_id": ErrorCodes.username_already_exists.value["code"]}}, 409
        if checking_mail_exist(email_id) is not None:
            return {"data": {"error": ErrorCodes.email_already_exists.value["msg"], "error_id": ErrorCodes.email_already_exists.value["code"]}}, 409

        return saving_user_to_db(username, email_id, password)
    except KeyError:
        return {"data": {"error": ErrorCodes.provide_all_signup_keys.value["msg"], "error_id": ErrorCodes.provide_all_signup_keys.value["code"]}}, 400


def send_message(users):
    msg = Message('OTP Validation', sender='seconds.clone@gmail.com', recipients=[users.email])
    otp = users.otp
    msg.body = f'Welcome to Seconds,\n THe otp for signin is {otp}'
    mail.send(msg)


def checking_username_exist(username):
    return User.query.filter_by(username=username).first()


def checking_mail_exist(email_id):
    return User.query.filter_by(email=email_id).first()


def saving_user_to_db(username, email_id, password):
    user_1 = User(username=username, email=email_id, hashed_password=hashing_password(password), is_admin=False, otp=generate_otp(), is_active=False)
    db.session.add(user_1)
    db.session.commit()
    profile_1 = UserProfile(None, None, None, photo='static/profile/profile.jpg', user_id=user_1.id)
    db.session.add(profile_1)
    db.session.commit()
    send_message(user_1)
    return {"data": {"message": "Otp ssend to the email"}}, 200


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
    val = True
    if len(passwd) < 8:
        val = False
    if len(passwd) > 20:
        val = False
    if not any(char.isdigit() for char in passwd):
        val = False
    if not any(char.isupper() for char in passwd):
        val = False
    if not any(char.islower() for char in passwd):
        val = False
    if not any(char in string.punctuation for char in passwd):
        val = False
    if val:
        return val


def check_username(username):
    user_name = "^[A-Za-z][A-Za-z0-9_]{7,29}$"
    if re.fullmatch(user_name, username):
        return True
    else:
        return False


@user.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email_id = data['email_id']
    otp = data['otp']
    user_a = User.query.filter(User.email == email_id).first()
    if not user_a:
        return {"data": {"error": "otp time out"}}, 400
    otp_send = user_a.otp
    if otp_send == otp:
        if user_a.created_at <= datetime.now() - timedelta(minutes=5):
            user_a.is_active=True
            db.session.add(user_a)
            db.session.commit()
        else:
            return {"data": {"error": "otp timed out"}}, 400
        return {"data": {"message": "Login successful"}}, 200
    else:
        return {"data": {"error": "otp verification failed"}}, 400


@user.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']

        if checking_username_exist(username) is None:
            return {"data": {"error": ErrorCodes.username_does_not_exist.value["msg"],
                             "error_id": ErrorCodes.username_does_not_exist.value["code"]}}, 400
        if password == "":
            return {"data": {"error": ErrorCodes.provide_password.value["msg"],
                             "error_id": ErrorCodes.provide_password.value["code"]}}, 400
        if checking_username_exist(username) and password_match(username, password):
            return checking_userpassword(username, password)
        return {"data": {"error": ErrorCodes.incorrect_password.value["msg"],
                         "error_id": ErrorCodes.incorrect_password.value["code"]}}, 409

    except KeyError:
        return {"data": {"error": ErrorCodes.provide_all_login_keys.value["msg"],
                         "error_id": ErrorCodes.provide_all_login_keys.value["code"]}}, 400


def password_match(username,password):
    return checking_2password(checking_username_exist(username).hashed_password, password)


def checking_userpassword(username, password):
    user_in = User.query.filter_by(username=username).first()
    if user_in and checking_2password(user_in.hashed_password, password):
        access_token = create_access_token(identity=user_in.id, fresh=True)
        refresh_token = create_refresh_token(identity=user_in.id)
        current_user = username
        return {"data": {"message": "Login successful"},"tokens": {"access_token": access_token,
                                                                   "refresh_token": refresh_token},
                "username": current_user,
                "is_admin": user_in.is_admin}, 200


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
    try:
        data = request.get_json()
        current_password = data['current_password']
        new_password = data['new_password']

        if not current_password:
            return {'data':{'error': ErrorCodes.provide_current_password.value['msg'],
                            "error_id": ErrorCodes.provide_current_password.value['code']}}, 400
        if not new_password:
            return {'data':{'error': ErrorCodes.provide_new_password.value['msg'],
                            "error_id": ErrorCodes.provide_new_password.value['code']}}, 400
        if not matching_password(user_id, current_password):
            return {"data": {"error" : ErrorCodes.incorrect_password.value['msg'],
                             "error_id": ErrorCodes.incorrect_password.value['code']}}, 400
        if not password_check(new_password):
            return {"data": {"error": ErrorCodes.password_format_not_matching.value["msg"],
                             'error_id': ErrorCodes.password_format_not_matching.value["code"]}}, 400
        if current_password == new_password:
            return {"data": {"error": ErrorCodes.new_password_should_not_be_same_as_previous_password.value["msg"],
                             "error_id": ErrorCodes.new_password_should_not_be_same_as_previous_password.value["code"]}}, 400

        return saving_new_password(user_id, new_password)
    except KeyError:
        return {"data": {"error": ErrorCodes.key_not_found.value["msg"],
                         "error_id": ErrorCodes.key_not_found.value["code"]}}, 400


def filter_user(user_id):
    return User.query.filter_by(id=user_id).first()


def matching_password(user_id, current_password):
    return checking_2password(filter_user(user_id).hashed_password, current_password)


def saving_new_password(user_id, new_password):
    filter_user(user_id).hashed_password = hashing_password(new_password)
    db.session.add(filter_user(user_id))
    db.session.commit()
    return {"data": {"message": "password changed successfully"}}, 200


def check_phone(phone):
    phone_num = "[6-9][0-9]{9}"
    return re.fullmatch(phone_num, phone)


jwt_redis_blocklist = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None


@user.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    jwt_redis_blocklist.set(jti, "", ex=app.config["JWT_ACCESS_TOKEN_EXPIRES"])
    return {"data": {"message": "Access token revoked"}}, 200


def allowed_profile_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png','jpg','jpeg'}


@user.route('/update_profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    photo = request.files.get('photo')
    name = request.form.get('name')
    email_id = request.form.get('email_id')
    phone = request.form.get('phone')
    address = request.form.get('address')
    if not name:
        return {'data': {'error': 'provide name'}}, 400
    if not email_id:
        return {'data': {'error': 'provide email_id'}}, 400
    if not email_id:
        return {'data': {'error': 'provide email_id'}}, 400
    if not check_email(email_id):
        return {'data': {'error': 'provide valid email_id'}}, 400
    if checking_new_and_old_mail_not_same(user_id,email_id):
        if checking_mail_exist(email_id):
            return {"data": {"error": ErrorCodes.email_already_exists.value["msg"],
                             "error_id": ErrorCodes.email_already_exists.value["code"]}}, 409
        else:
            filter_user(user_id).email = email_id
    if not phone:
        return {'data': {'error': 'provide phone number'}}, 400
    if not check_phone(phone):
        return {'data': {'error': 'phone number not valid'}}, 400
    if not address:
        return {'data': {'error': 'provide address'}}, 400
    if not photo:
        photo_url=UserProfile.query.filter_by(user_id=user_id).first().photo
    if photo and not allowed_profile_image_file(photo.filename):
        return {'data': {'error': 'image should be in png, jpg or jpeg format'}}, 400
    if photo and allowed_profile_image_file(photo.filename):
        filename = str(user_id)+secure_filename(photo.filename)
        if os.getenv('ENV') == "DEVELOPMENT":
            photo.save(os.path.join(app.config['UPLOADED_PROFILE_DEST'], filename))
        if os.getenv('ENV') == "PRODUCTION":
            s3.upload_fileobj(
                photo,
                app.config['S3_BUCKET'],
                'static/profile/'+filename,
                ExtraArgs={
                    "ACL": "public-read",
                    "ContentType": photo.content_type
                }
            )
        photo_url = 'static/profile/' + filename
    return saving_updated_profile(user_id, photo_url, name, phone, address)


def checking_new_and_old_mail_not_same(user_id,email_id):
    return filter_user(user_id).email != email_id


def saving_updated_profile(user_id, photo_url, name, phone, address):
    user_profile = UserProfile.query.filter_by(user_id=user_id).first()
    user_profile.photo = photo_url
    user_profile.name = name
    user_profile.phone = phone
    user_profile.address = address
    db.session.add(user_profile)
    db.session.add(filter_user(user_id))
    db.session.commit()
    return {'data': {'message': 'profile updated successfully'}}, 200


@user.route('/profile', methods=['GET'])
@jwt_required()
def view_profile():
    user_id=get_jwt_identity()
    return displaying_user_profile(user_id)


def displaying_user_profile(user_id):
    user_profile = UserProfile.query.filter_by(user_id=user_id).first()
    if os.getenv('ENV') == 'PRODUCTION':
        return {"data": {"message": [{"name": user_profile.name, "photo": app.config['S3_LOCATION']+user_profile.photo,
                                      "email_id": filter_user(user_id).email, "phone": user_profile.phone,
                                      "address": user_profile.address}]}}, 200
    if os.getenv('ENV') == 'DEVELOPMENT':
        return {"data": {"message": [{"is_admin": filter_user(user_id).is_admin, "name": user_profile.name,
                                      "photo": os.getenv('HOME_ROUTE') + user_profile.photo,
                                      "username": filter_user(user_id).username,
                                      "email_id": filter_user(user_id).email, "phone": user_profile.phone,
                                      "address": user_profile.address}]}}, 200
















































