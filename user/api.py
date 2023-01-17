from flask import request, Blueprint
from datetime import timedelta
from messages import ErrorCodes
from createapp import get_app
import re
import os
from user.models import User, UserProfile
from user.models import db
import bcrypt
import redis
from s3config import s3
from werkzeug.utils import secure_filename
from bcrypt import checkpw
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity,jwt_required,get_jwt
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
            return {"data" :{"error": ErrorCodes.email_cannot_be_empty.value["msg"], "error_id": ErrorCodes.email_cannot_be_empty.value["code"]}}, 400
        if not username:
            return {"data" :{"error": ErrorCodes.username_cannot_be_empty.value["msg"], "error_id": ErrorCodes.username_cannot_be_empty.value["code"]}}, 400
        if not password:
            return {"data":{"error": ErrorCodes.password_cannot_be_empty.value["msg"], "error_id": ErrorCodes.password_cannot_be_empty.value["code"]}}, 400
        if not check_email(email_id):
            return {"data" :{"error": ErrorCodes.provide_a_valid_email.value["msg"], "error_id": ErrorCodes.provide_a_valid_email.value["code"]}}, 400
        if not check_username(username):
            return {"data" :{"error": ErrorCodes.provide_a_valid_username.value["msg"], "error_id": ErrorCodes.provide_a_valid_username.value["code"]}}, 400
        if not password_check(password):
            return {"data" :{"error": ErrorCodes.password_format_not_matching.value["msg"] , "error_id": ErrorCodes.password_format_not_matching.value["code"]}}, 400
        if checking_username_exist(username) is not None:
            return {"data":{"error": ErrorCodes.username_already_exists.value["msg"], "error_id": ErrorCodes.username_already_exists.value["code"]}}, 409
        if checking_mail_exist(email_id) is not None:
            return {"data":{"error": ErrorCodes.email_already_exists.value["msg"], "error_id": ErrorCodes.email_already_exists.value["code"]}}, 409

        return saving_user_to_db(username, email_id, password)
    except KeyError:
        return {"data": {"error" : ErrorCodes.provide_all_signup_keys.value["msg"],"error_id": ErrorCodes.provide_all_signup_keys.value["code"]}}, 400

def checking_username_exist(username):
    return User.query.filter_by(username=username).first()

def checking_mail_exist(email_id):
    return User.query.filter_by(email=email_id).first()


def saving_user_to_db(username, email_id, password):
    user_1 = User(username=username, email=email_id, hashed_password=hashing_password(password), is_admin=False)
    db.session.add(user_1)
    db.session.commit()
    profile_1 = UserProfile(None, None, None, photo='static/profile/profile.jpg', user_id=user_1.id)
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

        if checking_username_exist(username) is None:
            return {"data": {"error": ErrorCodes.username_does_not_exist.value["msg"], "error_id": ErrorCodes.username_does_not_exist.value["code"]}}, 400
        if password == "":
            return {"data": {"error": ErrorCodes.provide_password.value["msg"], "error_id": ErrorCodes.provide_password.value["code"]}}, 400
        if checking_username_exist(username) and password_match(username,password):
            return checking_userpassword(username, password)
        return {"data": {"error": ErrorCodes.incorrect_password.value["msg"], "error_id": ErrorCodes.incorrect_password.value["code"]}}, 409

    except KeyError:
        return {"data": {"error": ErrorCodes.provide_all_login_keys.value["msg"], "error_id": ErrorCodes.provide_all_login_keys.value["code"]}}, 400


def password_match(username,password):
    return checking_2password(checking_username_exist(username).hashed_password, password)


def checking_userpassword(username, password):
    user_in = User.query.filter_by(username=username).first()
    if user_in and checking_2password(user_in.hashed_password, password):
        access_token = create_access_token(identity=user_in.id, fresh=True)
        refresh_token = create_refresh_token(identity=user_in.id)
        return {"data":
                    {"message": "Login successful"},"tokens": {"access_token": access_token,
                           "refresh_token": refresh_token}}, 200

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
            return {'data':{'error': ErrorCodes.provide_current_password.value['msg'], "error_id": ErrorCodes.provide_current_password.value['code']}}, 400
        if not new_password:
            return {'data':{'error': ErrorCodes.provide_new_password.value['msg'], "error_id": ErrorCodes.provide_new_password.value['code']}}, 400
        if not matching_password(user_id, current_password):
            return {"data": {"error" : ErrorCodes.incorrect_password.value['msg'], "error_id": ErrorCodes.incorrect_password.value['code']}}, 400
        if not password_check(new_password):
            return {"data": {"error": ErrorCodes.password_format_not_matching.value["msg"], 'error_id': ErrorCodes.password_format_not_matching.value["code"]}}, 400
        if current_password==new_password:
            return {"data": {"error": ErrorCodes.new_password_should_not_be_same_as_previous_password.value["msg"], "error_id": ErrorCodes.new_password_should_not_be_same_as_previous_password.value["code"]}}, 400

        return saving_new_password(user_id, new_password)
    except KeyError:
        return {"data": {"error": ErrorCodes.key_not_found.value["msg"], "error_id": ErrorCodes.key_not_found.value["code"]}}, 400

def filter_user(user_id):
    return User.query.filter_by(id=user_id).first()


def matching_password(user_id,current_password):
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
    jwt_redis_blocklist.set(jti, "", ex=timedelta(minutes=30))
    return {"data":{"message":"Access token revoked"}}

def allowed_profile_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png','jpg','jpeg'}

@user.route('/update_profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id=get_jwt_identity()
    photo=request.files.get('photo')
    name=request.form.get('name')
    email_id=request.form.get('email_id')
    phone = request.form.get('phone')
    address = request.form.get('address')
    if not name:
        return {'data': {'error': 'provide name'}}
    if not email_id:
        return {'data': {'error': 'provide email_id'}}
    if not email_id:
        return {'data': {'error': 'provide email_id'}}
    if not check_email(email_id):
        return {'data': {'error': 'provide valid email_id'}}
    if checking_new_and_old_mail_not_same(user_id,email_id):
        if checking_mail_exist(email_id):
            return {"data": {"message":"email id already exist"}}
        else:
            filter_user(user_id).email = email_id
    if not phone:
        return {'data': {'error': 'provide phone number'}}
    if not check_phone(phone):
        return {'data': {'error': 'phone number not valid'}}
    if not address:
        return {'data': {'error': 'provide address'}}
    if not photo:
        photo_url=UserProfile.query.filter_by(user_id=user_id).first().photo
    if photo and not allowed_profile_image_file(photo.filename):
        return {'data': {'error': 'image should be in png, jpg or jpeg format'}}
    if photo and allowed_profile_image_file(photo.filename):
        filename = str(user_id)+secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOADED_PROFILE_DEST'], filename))
        # s3.upload_fileobj(
        #     photo,
        #     app.config['S3_BUCKET'],
        #     'static/profile/'+filename,
        #     ExtraArgs={
        #         "ACL": "public-read",
        #         "ContentType": photo.content_type
        #     }
        # )
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
    return {'data': {'message': 'profile updated successfully'}}

@user.route('/profile', methods=['GET'])
@jwt_required()
def view_profile():
    user_id=get_jwt_identity()
    return displaying_user_profile(user_id)
def displaying_user_profile(user_id):
    user_profile=UserProfile.query.filter_by(user_id=user_id).first()
    # return {"data":{"message": [{"name": user_profile.name, "photo": app.config['S3_LOCATION']+user_profile.photo, "email_id": filter_user(user_id).email, "phone": user_profile.phone, "address": user_profile.address}]}}
    return {"data": {"message": [{"name": user_profile.name, "photo": os.getenv('HOME_ROUTE') + user_profile.photo, "email_id": filter_user(user_id).email, "phone": user_profile.phone, "address": user_profile.address}]}}

# @user.route('/upload_images', methods=['POST'])
# def update_profile1():
#     photo=request.files.get('photo')
#     if photo and allowed_profile_image_file(photo.filename):
#         filename = secure_filename(photo.filename)
#         s3.upload_fileobj(
#              photo,
#              app.config['S3_BUCKET'],
#              'static/profile/'+filename,
#             ExtraArgs={
#                     "ACL": "public-read",
#                     "ContentType": photo.content_type
#             })
#         photo_url = 'static/profile/' + filename
#         return "IMAGE_UPLOADED"
#
# @user.route('/upload', methods=['GET'])
# def update_profile2():
#
#     return {"IMAGE": app.config['S3_LOCATION']+'static/profile/download.jpeg'}















































