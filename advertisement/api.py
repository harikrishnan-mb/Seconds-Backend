from flask import Blueprint, request
from s3config import s3
from advertisement.models import db, Category, Advertisement, AdImage, AdPlan, FavouriteAd, ReportAd, Message,\
    Notification, Chatroom
from user.api import check_email, check_phone
from user.models import User, UserProfile
from user.api import get_jwt_identity, jwt_required, verify_jwt_in_request
from geoalchemy2 import WKTElement
from messages import ErrorCodes
from flask_socketio import SocketIO, emit, join_room, leave_room
from advertisement.mocked_db import get_every_categories, get_only_categories, admin_is_true, deleting_the_category, \
    checking_category_name_already_exist, checking_parent_id_exist, adding_category_to_db,\
    checking_new_and_old_category_name_not_same, filtering_category, updating_category_in_db, \
    ads_plan, checking_user_posted_ad, deleting_ad, filtering_ad_by_id, saving_created_ad, updating_ad_details
import os
from datetime import datetime, timedelta
import secrets
import string
from sqlalchemy import func, or_, and_
from werkzeug.utils import secure_filename
from createapp import get_app
from dotenv import load_dotenv
load_dotenv()
app = get_app()
socketio = SocketIO(app, cors_allowed_origins="*")
#  async_mode="asyncio",
ad = Blueprint('ad', __name__)


@ad.route("/list_every_category", methods=["GET"])
def list_every_category():
    categories_list = []
    return get_every_categories(categories_list)


@ad.route("/category", methods=["GET"])
def list_category():
    categories_list = []
    return get_only_categories(categories_list)


@ad.route("/category_delete/<int:category_id>", methods=["DELETE"])
@jwt_required()
def delete_category(category_id):
    person = get_jwt_identity()
    if admin_is_true(person) is True:
        if filtering_category(category_id):
            try:
                os.remove(os.path.join(app.config['UPLOADED_ITEMS_DEST'], filtering_category(category_id).image))
            except:
                pass
            return deleting_the_category(category_id)
        else:
            return {"data": {"error": "category does not exist"}}, 400
    else:
        return {"data": {"error": "only admin can access this route"}}, 400


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'svg'}


@ad.route("/add_category", methods=["POST"])
@jwt_required()
def add_category():
    person = get_jwt_identity()
    if admin_is_true(person) is True:
        category = request.form.get("category")
        file = request.files.get('file')
        parent_id = request.form["parent_id"]
        if not category:
            return {"data": {"error": "provide category name"}}, 400
        if not file and not parent_id:
            return {"data": {"error": "provide parent_id or file"}}, 400
        if parent_id and file:
            return {"data": {"error": "provide image if category and provide parent_id if sub category"}}, 400
        if parent_id:
            try:
                parent_id=float(parent_id)
            except ValueError:
                return {"data": {"error":"parent_id should be integer"}}, 400
        if checking_category_name_already_exist(category):
            return {"data": {"error": "category already exist"}}, 400
        if parent_id:
            if not checking_parent_id_exist(parent_id):
                return {"data": {"error": "parent_id should be id of any category"}}, 400
            else:
                category_add = Category(name=category, image="", parent_id=parent_id)
        if not parent_id or parent_id == '':
            if not allowed_file(file.filename):
                return {"data": {"error": "image should be svg"}}, 400
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                if os.getenv('ENV') == "DEVELOPMENT":
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                if os.getenv('ENV') == "PRODUCTION":
                    s3.upload_fileobj(file, app.config['S3_BUCKET'], 'static/catagory/' + filename,
                                      ExtraArgs={"ACL": "public-read","ContentType": file.content_type})
                category_add = Category(name=category, image='static/catagory/' + filename, parent_id=None)
        return adding_category_to_db(category_add)
    else:
        return {"data": {"error": "only admin can add category"}}, 400


@ad.route("/update_category/<int:category_id>", methods=["PUT"])
@jwt_required()
def change_category(category_id):
    person = get_jwt_identity()
    if admin_is_true(person) is True:
        if filtering_category(category_id):
            category = request.form.get("category")
            file = request.files.get('file')
            parent_id = request.form["parent_id"]
            if not category:
                return {"data": {"error": "provide category name"}}, 400
            if checking_new_and_old_category_name_not_same(category_id, category):
                if checking_category_name_already_exist(category):
                    return {"data": {"error": "category already exist"}}, 400
                else:
                    filtering_category(category_id).name = category
            if not file and not parent_id:
                return {"data": {"error": "provide parent_id or file"}}, 400
            if parent_id and file:
                return {"data": {"error": "provide image if category and provide parent_id if sub category"}}, 400
            if parent_id:
                try:
                    parent_id = float(parent_id)
                except ValueError:
                    return {"data": {"error": "parent_id should be integer"}}, 400
            if parent_id:
                # check_ids = Category.query.filter_by(id=parent_id).first()
                if not checking_parent_id_exist(parent_id):
                    return {"data": {"error": "parent_id should be id of any category"}}, 400

                filtering_category(category_id).image = ''
                filtering_category(category_id).parent_id = parent_id
            if not parent_id or parent_id == '':
                if not allowed_file(file.filename):
                    return {"data": {"error": "image should be svg"}}, 400
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    if os.getenv("ENV") == "DEVELOPMENT":
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    if os.getenv("ENV") == "PRODUCTION":
                        s3.upload_fileobj(file, app.config['S3_BUCKET'], 'static/catagory/' + filename,
                                          ExtraArgs={"ACL": "public-read", "ContentType": file.content_type})

                    filtering_category(category_id).image = 'static/catagory/' + filename
                    filtering_category(category_id).parent_id = None
            return updating_category_in_db(category_id)
        else:
            return {"data": {"error": "category id does not exist"}}, 400
    else:
        return {"data": {"error": "only admin can update category"}}, 400


@ad.route("/ad_plan", methods=["GET"])
def list_ad_plan():
    ad_plan_list = []
    return ads_plan(ad_plan_list)


def allowed_img_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png','jpg','jpeg','webp'}


def generate_random_text():
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(14))


@ad.route("/reactivate_ad/<int:ad_id>", methods=["PUT"])
@jwt_required()
def making_ad_active(ad_id):
    person = get_jwt_identity()
    if filtering_ad_by_id(ad_id) is None:
        return {"data": {"error": "ad not found"}}, 400
    if checking_user_posted_ad(ad_id, person):
        return saving_ad_as_active(ad_id)
    return {"data": {"error": "only owner can edit ad"}}, 400


def saving_ad_as_active(ad_id):
    filtering_ad_by_id(ad_id).status = "active"
    db.session.add(filtering_ad_by_id(ad_id))
    db.session.commit()
    return {"data": {"message": "ad activated"}}, 200


@ad.route("/delete_ad/<int:del_ad_id>", methods=["DELETE"])
@jwt_required()
def delete_ad(del_ad_id):
    person = get_jwt_identity()
    if filtering_ad_by_id(del_ad_id) is None:
        return {"data": {"error": "ad not found"}}, 400
    if checking_user_posted_ad(del_ad_id, person):
        return deleting_ad(del_ad_id)
    return {"data": {"error": "invalid request"}}, 400


@ad.route("/create_ad", methods=["POST"])
@jwt_required()
def create_ad():
    person = get_jwt_identity()
    category_id = request.form.get("category_id")
    status = request.form.get("status")
    images = request.files.getlist('images')
    title = request.form.get("title")
    seller_type = request.form.get("seller_type")
    description = request.form.get("description")
    price = request.form.get("price")
    ad_plan_id = request.form.get("ad_plan_id")
    negotiable_product = request.form.get("negotiable_product")
    feature_product = request.form.get("feature_product")
    location = request.form.get("location")
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")
    seller_name = request.form.get("seller_name")
    phone = request.form.get("phone")
    email_id = request.form.get("email_id")
    if not category_id:
        return {"data":{"error": "provide category id"}}, 400
    try:
        category_id=int(category_id)
    except ValueError:
        return {"data": {"error": "provide category id as integer"}}, 400
    if checking_category_id_exist(category_id) is None:
        return {"data": {"error": "category id not found"}}, 400
    if not images:
        return {"data": {"error": ErrorCodes.image_field_is_required.value['msg'],
                         'error_id': ErrorCodes.image_field_is_required.value['code']}}, 400
    for image in images:
        if not image:
            return {"data": {"error": "provide image"}}, 400
        if image and not allowed_img_file(image.filename):
            return {"data": {"error": ErrorCodes.image_should_be_in_png_webp_jpg_or_jpeg_format.value['msg'],
                             "error_id": ErrorCodes.image_should_be_in_png_webp_jpg_or_jpeg_format.value['code']}}, 400
    if not title:
        return {"data": {"error": "provide title"}}, 400
    if not status:
        status = 'active'
    if not seller_type:
        return {"data": {"error": "provide seller_type"}}, 400
    if not description:
        description = ''
    if not price:
        return {"data": {"error": "provide price"}}, 400
    try:
        price = float(price)
    except ValueError:
        return {"data": {"error": "provide price as floating number"}}, 400
    if not negotiable_product:
        return {"data": {"error": "provide product is negotiable or not"}}, 400
    if negotiable_product.capitalize() == "True":
        negotiable_product = True
    elif negotiable_product.capitalize() == "False":
        negotiable_product = False
    else:
        return {"data": {"error": "provide product is negotiable or not as True or False"}}, 400
    if not feature_product:
        return {"data": {"error": "provide product is featured or not"}}, 400
    if feature_product.capitalize() == "True":
        feature_product = True
        if not ad_plan_id:
            return {"data": {"error": "provide advertisement plan id"}}, 400
        try:
            ad_plan_id = int(ad_plan_id)
        except ValueError:
            return {"data": {"error": "provide advertisement plan id as integer"}}, 400
        if not checking_adplan_exist(ad_plan_id):
            return {"data": {"error": "advertisement plan id not found"}}, 400
    elif feature_product.capitalize() == "False":
        feature_product = False
        ad_plan_id = None
    else:
        return {"data": {"error": "provide product is featured or not as True or False"}}, 400
    if not location:
        return {"data": {"error": "provide location"}}, 400
    if not latitude:
        return {"data": {"error": "provide latitude"}}, 400
    try:
        latitude = float(latitude)
    except ValueError:
        return {"data": {"error": "provide latitude as floating number"}}, 400
    if not longitude:
        return {"data": {"error": "provide longitude"}}, 400
    try:
        longitude = float(longitude)
    except ValueError:
        return {"data": {"error": "provide longitude as floating number"}}, 400
    if not seller_name:
        return {"data": {"error": "provide seller_name"}}, 400
    if not phone:
        return {"data": {"error": "provide phone number"}}, 400
    if not check_phone(phone):
        return {"data": {"error": "provide valid phone number"}}, 400
    if not email_id:
        email_id=''
    if email_id and not check_email(email_id):
        return {"data": {"error": "provide valid email"}}, 400
    geo = WKTElement('POINT({} {})'.format(str(longitude), str(latitude)))

    return saving_created_ad(title, description, category_id, status, seller_type, price, ad_plan_id,
                             negotiable_product, feature_product, location, latitude, longitude, seller_name, phone,
                             email_id, images, geo)


def checking_category_id_exist(category_id):
    return Category.query.filter_by(id=int(category_id)).first()


def checking_adplan_exist(ad_plan_id):
    return AdPlan.query.filter_by(id=ad_plan_id).first()


@ad.route("/view_ad/<int:page>", methods=["GET"])
def view_ad(page):
    verify_jwt_in_request(optional=True)
    sorts = [Advertisement.is_featured.desc()]
    filter_list = [Advertisement.status == "active", Advertisement.is_deleted == False, Advertisement.is_disabled == False]
    count_list = [Advertisement.status == "active", Advertisement.is_deleted == False, Advertisement.is_disabled == False]

    if "type_of" in request.args:
        type_of = request.args["type_of"]
        if type_of == 'my_ads':
            if "Authorization" in request.headers:
                person = get_jwt_identity()
                query = Advertisement.user_id == person
                filter_list = [Advertisement.is_deleted == False]
                count_list = [Advertisement.is_deleted == False]
                filter_list.append(query)
                count_list.append(query)
                if "sort" in request.args:
                    sort = request.args["sort"]
                    if sort == "active":
                        query = Advertisement.status == "active"
                        filter_list.append(query)
                        count_list.append(query)
                    elif sort == "inactive":
                        query = Advertisement.status == "inactive"
                        filter_list.append(query)
                        count_list.append(query)
            else:
                return {"data": {"message": "only authenticated users can view my ads"}}, 401

        if type_of == 'my_fav':
            if "Authorization" in request.headers:
                person = get_jwt_identity()
                favourite_list = []
                favourites = FavouriteAd.query.filter_by(user_id=person).order_by(FavouriteAd.created_at.desc()).all()
                if favourites:
                    for fav in favourites:
                        query = Advertisement.id == fav.ad_id
                        favourite_list.append(query)
                    filter_list.append(or_(*favourite_list))
                    count_list.append(or_(*favourite_list))
                else:
                    filter_list.append(None)
                    count_list.append(None)
            else:
                return {"data": {"message": "only authenticated users can view my ads"}}, 401
        else:
            pass

    # filtering based on min_price, max_price, main_category_id and subcategory_id
    if "max_price" in request.args:
        max_price = request.args["max_price"]
        price = Advertisement.price <= max_price
        filter_list.append(price)
    if "min_price" in request.args:
        min_price = request.args["min_price"]
        price = Advertisement.price >= min_price
        filter_list.append(price)
    if "category_id" in request.args:
        category_id = request.args["category_id"]
        category_id = category_id.split(',')
        category_map = map(int, category_id)
        category_id_list = list(category_map)
        cat_id = Advertisement.category_id.in_(category_id_list)
        filter_list.append(cat_id)
    if "main_category_id" in request.args:
        main_category_id = request.args["main_category_id"]
        main_category_id = main_category_id.split(',')
        main_category_map = map(int, main_category_id)
        categories_list = list(main_category_map)
        sub_category_list = []
        for category_id in categories_list:
            sub_categories = Category.query.filter_by(parent_id=category_id).all()
            for sub_category in sub_categories:
                sub_category_list.append(sub_category.id)
        category_ids = Advertisement.category_id.in_(sub_category_list)
        filter_list.append(category_ids)
        count_list.append(category_ids)

    # sorting based on time, price: high to low and price: low to high
    if "sort" in request.args:
        sort = request.args["sort"]
        if sort == "time":
            sort_1 = Advertisement.created_at.desc()
            sorts.append(sort_1)
        if sort == "hightolow":
            sort_1 = Advertisement.price.desc()
            sorts.append(sort_1)
        if sort == "lowtohigh":
            sort_1 = Advertisement.price.asc()
            sorts.append(sort_1)
    if "sort" not in request.args:
        sorts.append(Advertisement.created_at.desc())

    # location based filtering
    if "lat" and "long" in request.args:
        lat = request.args["lat"]
        long = request.args["long"]
        loc_point = WKTElement('POINT({} {})'.format(str(long), str(lat)))
        loc_radius = 20000
        query = (func.ST_Distance(Advertisement.geo, loc_point) < loc_radius)
        filter_list.append(query)
        count_list.append(query)

    # searching
    if "search" in request.args:
        search = request.args["search"]
        search_lists = search.split(' ')
        searching_the_ad(search_lists, filter_list, count_list)

    list_ad = []
    return listing_the_ad(filter_list, sorts, list_ad, page, count_list)


def searching_the_ad(search_lists, filter_list, count_list):
    for search_list in search_lists:
        ads = Advertisement.query.filter(func.lower(Advertisement.title).contains(func.lower(search_list))).first()
        categories = Category.query.filter(func.lower(Category.name).contains(func.lower(search_list))).first()
        if ads and categories:
            search_query = or_(func.lower(Advertisement.title).contains(func.lower(search_list)), Advertisement.category_id == categories.id)
        elif ads:
            search_query = func.lower(Advertisement.title).contains(func.lower(search_list))
        elif categories:
            search_query = Advertisement.category_id == categories.id
        else:
            search_query = None
        filter_list.append(search_query)
        count_list.append(search_query)
    return filter_list, count_list


def listing_the_ad(filter_list, sorts, list_ad, page, count_list):
    adv = Advertisement.query.filter_by(is_featured=True).all()
    for ads in adv:
        plan = AdPlan.query.filter_by(id=ads.advertising_plan_id).first()
        if datetime.now()-ads.created_at > timedelta(days=plan.days):
            ads.is_featured = False
            db.session.add(ads)
            db.session.commit()
    count_of_price_range_0_to_1_lakh = Advertisement.query.filter(*count_list, and_(Advertisement.price >= 0, Advertisement.price < 100000)).count()
    count_of_price_range_1_to_3_lakh = Advertisement.query.filter(*count_list, and_(Advertisement.price >= 100000, Advertisement.price < 300000)).count()
    count_of_price_range_3_to_6_lakh = Advertisement.query.filter(*count_list, and_(Advertisement.price >= 300000, Advertisement.price < 600000)).count()
    count_of_price_range_greater_than_6_lakh = Advertisement.query.filter(*count_list, and_(Advertisement.price >= 600000)).count()
    advertisements = Advertisement.query.filter(*filter_list).order_by(*sorts).paginate(page=page, per_page=12, error_out=False)
    number_of_ads = Advertisement.query.filter(*filter_list).count()
    for advertisement in advertisements:
        is_liked = False
        created_by_me = False
        if "Authorization" in request.headers:
            person = get_jwt_identity()
            filter_list.append(Advertisement.user_id != person)
            count_list.append(Advertisement.user_id != person)
            if FavouriteAd.query.filter_by(ad_id=advertisement.id, user_id=person).first():
                is_liked = True
            if person == advertisement.user_id:
                created_by_me = True
        ad_images = AdImage.query.filter_by(ad_id=advertisement.id, is_cover_image=True).first()
        if os.getenv('ENV') == 'DEVELOPMENT':
            images = os.getenv('HOME_ROUTE') + ad_images.file
        if os.getenv('ENV') == 'PRODUCTION':
            images = app.config['S3_LOCATION'] + ad_images.file
        ad_filter = {"id": advertisement.id, "title": advertisement.title, "cover_image": images,
                     "featured": advertisement.is_featured, "location": advertisement.location,
                     "price": advertisement.price, "status": advertisement.status, "favourite": is_liked, "created_by_me": created_by_me}
        list_ad.append(ad_filter)
    return {"data": {"message": list_ad, "count": number_of_ads, "below_one_lakh": count_of_price_range_0_to_1_lakh,
                     "one_to_three_lakh": count_of_price_range_1_to_3_lakh,
                     "three_to_six_lakh": count_of_price_range_3_to_6_lakh,
                     "above_six_lakh": count_of_price_range_greater_than_6_lakh}}, 200


@ad.route("/update_ad/<int:ads_id>", methods=["PUT"])
@jwt_required()
def update_ad(ads_id):
    person = get_jwt_identity()
    if checking_user_posted_ad(ads_id, person):
        category_id = request.form.get("category_id")
        status = request.form.get("status")
        images = request.files.getlist('images')
        title = request.form.get("title")
        seller_type = request.form.get("seller_type")
        description = request.form.get("description")
        price = request.form.get("price")
        ad_plan_id = request.form.get("ad_plan_id")
        negotiable_product = request.form.get("negotiable_product")
        feature_product = request.form.get("feature_product")
        location = request.form.get("location")
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        seller_name = request.form.get("seller_name")
        phone = request.form.get("phone")
        email_id = request.form.get("email_id")
        if not category_id:
            return {"data": {"error": "provide category id"}}, 400
        if not images:
            return {"data": {"error": ErrorCodes.image_field_is_required.value['msg'],
                             'error_id': ErrorCodes.image_field_is_required.value['code']}}, 400
        for image in images:
            if image.filename == '':
                return {"data": {"error": "provide image"}}, 400
            if image and not allowed_img_file(image.filename):
                return {"data": {"error": ErrorCodes.image_should_be_in_png_webp_jpg_or_jpeg_format.value['msg'],
                                 "error_id": ErrorCodes.image_should_be_in_png_webp_jpg_or_jpeg_format.value['code']}}, 400
        try:
            category_id = int(category_id)
        except ValueError:
            return {"data": {"error": "provide category id as integer"}}, 400
        if checking_category_id_exist(category_id) is None:
            return {"data": {"error": "category id not found"}}, 400
        if not title:
            return {"data": {"error": "provide title"}}, 400
        if not status:
            status = 'active'
        if not seller_type:
            return {"data": {"error": "provide seller_type"}}, 400
        if not description:
            description = ''
        if not price:
            return {"data": {"error": "provide price"}}, 400
        try:
            price = float(price)
        except ValueError:
            return {"data": {"error": "provide price as floating number"}}, 400
        if not negotiable_product:
            return {"data": {"error": "provide product is negotiable or not"}}, 400
        if negotiable_product.capitalize() == "True":
            negotiable_product = True
        elif negotiable_product.capitalize() == "False":
            negotiable_product = False
        else:
            return {"data": {"error": "provide product is negotiable or not as True or False"}}, 400
        if not feature_product:
            return {"data": {"error": "provide product is featured or not"}}, 400
        if feature_product.capitalize() == "True":
            feature_product = True
            if not ad_plan_id:
                return {"data": {"error": "provide advertisement plan id"}}, 400
            try:
                ad_plan_id = int(ad_plan_id)
            except ValueError:
                return {"data": {"error": "provide advertisement plan id as integer"}}, 400
            if not checking_adplan_exist(ad_plan_id):
                return {"data": {"error": "advertisement plan id not found"}}, 400
        elif feature_product.capitalize() == "False":
            feature_product = False
            ad_plan_id = None
        else:
            return {"data": {"error": "provide product is featured or not as True or False"}}, 400
        if not location:
            return {"data": {"error": "provide location"}}, 400
        if not latitude:
            return {"data": {"error": "provide latitude"}}, 400
        try:
            latitude = float(latitude)
        except ValueError:
            return {"data": {"error": "provide latitude as floating number"}}, 400
        if not longitude:
            return {"data": {"error": "provide longitude"}}, 400
        try:
            longitude = float(longitude)
        except ValueError:
            return {"data": {"error": "provide longitude as floating number"}}, 400
        if float(longitude) is False:
            return {"data": {"error": "provide longitude as floating number"}}, 400
        if not seller_name:
            return {"data": {"error": "provide seller_name"}}, 400
        if not phone:
            return {"data": {"error": "provide phone number"}}, 400
        if not check_phone(phone):
            return {"data": {"error": "provide valid phone number"}}, 400
        if not email_id:
            email_id=''
        if email_id and not check_email(email_id):
            return {"data": {"error": "provide valid email"}}, 400
        geo = WKTElement('POINT({} {})'.format(str(longitude), str(latitude)))
        return updating_ad_details(title, person, description, category_id, status, seller_type, price, ad_plan_id,
                                   negotiable_product, feature_product, location, latitude, longitude, seller_name,
                                   phone, email_id, images, ads_id, geo)
    else:
        return{"data": {"error": "only owner can edit ad"}}, 400


@ad.route("/ad_details/<int:ad_id>", methods=["GET"])
def details_of_ad(ad_id):
    if filtering_ad_by_id(ad_id) is None:
        return {"data": {"error": "ad not found"}}, 400
    image_list = []
    is_liked = False
    created_by_me = False
    if "Authorization" in request.headers:
        verify_jwt_in_request()
        person = get_jwt_identity()
        if FavouriteAd.query.filter_by(ad_id=ad_id, user_id=person).first():
            is_liked = True
        if Advertisement.query.filter(Advertisement.id == ad_id, Advertisement.user_id == person).first():
            created_by_me = True
    return returning_ad_detail(image_list, ad_id, is_liked,created_by_me)


def filtering_user_created_ad(ad_id):
    return UserProfile.query.filter_by(user_id=filtering_ad_by_id(ad_id).user_id).first()


def filtering_image_of_ad(ad_id):
    return AdImage.query.filter_by(ad_id=ad_id).all()


def filtering_category_id_of_ad(ad_id):
    sub_category=Category.query.filter_by(id=filtering_ad_by_id(ad_id).category_id).first()
    return Category.query.filter_by(id=sub_category.parent_id).first().id


def filtering_category_image_of_ad(ad_id):
    sub_category = Category.query.filter_by(id=filtering_ad_by_id(ad_id).category_id).first()
    return Category.query.filter_by(id=sub_category.parent_id).first().image


def filtering_category_name_of_ad(ad_id):
    sub_category = Category.query.filter_by(id=filtering_ad_by_id(ad_id).category_id).first()
    return Category.query.filter_by(id=sub_category.parent_id).first().name


def filtering_sub_category_name_of_ad(ad_id):
    return Category.query.filter_by(id=filtering_ad_by_id(ad_id).category_id).first().name


def returning_ad_detail(image_list, ad_id, is_liked,created_by_me):
    for ad_image in filtering_image_of_ad(ad_id):
        if os.getenv('ENV')=='DEVELOPMENT':
            image_list.append(os.getenv('HOME_ROUTE')+ad_image.file)
        if os.getenv('ENV') == 'PRODUCTION':
            image_list.append(app.config['S3_LOCATION'] + ad_image.file)
    if os.getenv('ENV') == 'DEVELOPMENT':
        images = os.getenv('HOME_ROUTE') + filtering_user_created_ad(ad_id).photo
    if os.getenv('ENV') == 'PRODUCTION':
        images = app.config['S3_LOCATION'] + filtering_user_created_ad(ad_id).photo
    return {"id": filtering_ad_by_id(ad_id).id, "title": filtering_ad_by_id(ad_id).title,
            "description": filtering_ad_by_id(ad_id).description,
            "advertising_id": filtering_ad_by_id(ad_id).advertising_id, "images": image_list,
            "seller_name": filtering_ad_by_id(ad_id).seller_name, "featured": filtering_ad_by_id(ad_id).is_featured,
            "latitude":filtering_ad_by_id(ad_id).latitude, "longitude": filtering_ad_by_id(ad_id).longitude,
            "location": filtering_ad_by_id(ad_id).location, "price": filtering_ad_by_id(ad_id).price,
            "posted_at": filtering_ad_by_id(ad_id).created_at, "photo": images,
            "status": filtering_ad_by_id(ad_id).status, "favourite": is_liked,
            "category_id": filtering_category_id_of_ad(ad_id), "category_name": filtering_category_name_of_ad(ad_id),
            "created_by_me": created_by_me, "sub_category_id": filtering_ad_by_id(ad_id).category_id,
            "negotiable": filtering_ad_by_id(ad_id).is_negotiable,
            "seller_type": filtering_ad_by_id(ad_id).seller_type,
            "ad_plan_id": filtering_ad_by_id(ad_id).advertising_plan_id, "phone": filtering_ad_by_id(ad_id).phone,
            "email_id": filtering_ad_by_id(ad_id).email, "sub_category_name": filtering_sub_category_name_of_ad(ad_id),
            "category_image": os.getenv('HOME_ROUTE')+filtering_category_image_of_ad(ad_id)}, 200


@ad.route("/similar_ads/<int:ad_id>/<int:page>", methods=["GET"])
def recommended_ad(ad_id, page):
    if filtering_ad_by_id(ad_id) is None:
        return {"data": {"error": "ad not found"}}, 400
    sorts = [Advertisement.is_featured.desc()]
    filter_list = [Advertisement.status == "active", Advertisement.is_deleted == False, Advertisement.is_disabled == False, Advertisement.id!=ad_id]
    search_list = []
    titles_list=splitting_title(ad_id,sorts).split(' ')
    searching_in_title_list(titles_list, search_list)
    searching_the_category_id(ad_id,search_list)
    filter_list.append(or_(*search_list))
    list_recommended_ad=[]
    for advertisement in returning_similar_ads(page,filter_list,sorts):
        is_liked = False
        if "Authorization" in request.headers:
            verify_jwt_in_request()
            person = get_jwt_identity()
            if checking_user_liked_ad(advertisement, person):
                is_liked = True
        showing_similar_ads(advertisement, is_liked, list_recommended_ad)
    return {"data": {"message": list_recommended_ad }}, 200


def splitting_title(ad_id, sorts):
    sorts_query = func.ST_Distance(Advertisement.geo, filtering_ad_by_id(ad_id).geo).asc()
    sorts.append(sorts_query)
    return filtering_ad_by_id(ad_id).title


def searching_in_title_list(titles_list, search_list):
    for title in titles_list:
        if Advertisement.query.filter(func.lower(Advertisement.title).contains(func.lower(title))).first():
            filters = func.lower(Advertisement.title).contains(func.lower(title))
            search_list.append(filters)
        else:
            search_list = search_list
    return search_list


def searching_the_category_id(ad_id,search_list):
    category_ids = Advertisement.category_id == filtering_ad_by_id(ad_id).category_id
    return search_list.append(category_ids)


def returning_similar_ads(page,filter_list,sorts):
    return Advertisement.query.filter(*filter_list).order_by(*sorts).paginate(page=page, per_page=10,error_out=False)


def showing_similar_ads(advertisement,is_liked,list_recommended_ad):
    ad_images = AdImage.query.filter_by(ad_id=advertisement.id, is_cover_image=True).first()
    if os.getenv('ENV') == 'DEVELOPMENT':
        images = os.getenv('HOME_ROUTE') + ad_images.file
    if os.getenv('ENV') == 'PRODUCTION':
        images = app.config['S3_LOCATION'] + ad_images.file
    ad_filter = {"id": advertisement.id, "title": advertisement.title,
                 "cover_image": images, "featured": advertisement.is_featured,
                 "location": advertisement.location, "price": advertisement.price,
                 "status": advertisement.status, "favourite": is_liked}
    return list_recommended_ad.append(ad_filter)


@ad.route("/remove_ad/<int:ad_id>", methods=["PUT"])
@jwt_required()
def making_ad_inactive(ad_id):
    person = get_jwt_identity()
    if filtering_ad_by_id(ad_id) is None:
        return {"data": {"error": "ad not found"}}, 400
    if checking_user_posted_ad(ad_id, person):
        return saving_ad_as_inactive(ad_id)
    return {"data": {"error": "only owner can edit ad"}}, 400


def saving_ad_as_inactive(ad_id):
    filtering_ad_by_id(ad_id).status = "inactive"
    db.session.add(filtering_ad_by_id(ad_id))
    db.session.commit()
    return {"data": {"message": "ad inactivated"}}, 200


@ad.route("/favourite_ad/<int:ad_id>", methods=["POST"])
@jwt_required()
def favourite_ad(ad_id):
    person = get_jwt_identity()
    if filtering_ad_by_id(ad_id) is None:
        return {"data": {"error": "ad not found"}}, 400
    if checking_user_favourited_ad(person, ad_id):
        return removing_ad_from_favourite(person, ad_id)
    favourite = FavouriteAd(ad_id=ad_id, user_id=person)
    return saving_ad_to_favourite(favourite, ad_id, person)


def checking_user_favourited_ad(person, ad_id):
    return FavouriteAd.query.filter_by(ad_id=ad_id, user_id=person).first()


def removing_ad_from_favourite(person, ad_id):
    ads = Advertisement.query.filter(Advertisement.id == ad_id).first()
    owner_id = ads.user_id
    db.session.delete(checking_user_favourited_ad(person, ad_id))
    if person != owner_id:
        notification = Notification.query.filter(Notification.receiver_id == owner_id, Notification.ad_id == ad_id).first()
        db.session.delete(notification)
    db.session.commit()
    return {"data": {"message": "ad removed from favourites"}}, 200


def saving_ad_to_favourite(favourite, ad_id, person):
    username = User.query.filter(User.id == person).first().username
    ads = Advertisement.query.filter(Advertisement.id == ad_id).first()
    title = ads.title
    user_id = ads.user_id
    if person != user_id:
        content = f'{username} has favorited your ad titled as {title}'
        notifications = Notification(receiver_id=user_id, content=content, ad_id=ad_id)
        db.session.add(notifications)
    db.session.add(favourite)
    db.session.commit()
    # notif = Notification.query.filter(Notification.receiver_id == ads.user_id, Notification.is_read == False).count()
    # user_room = 'user_{}'.format(person)
    # emit('response',
    #      {'message': 'New notifications',
    #       'count': notif,
    #       'notification': content},
    #      room=user_room,
    #      namespace='/notification')
    return {"data": {"message": "ad saved to favourites"}}, 200


@ad.route("/view_ad", methods=["GET"])
@jwt_required()
def getting_my_ads():
    person=get_jwt_identity()
    my_advertisement_list=[]
    if advertisement_created_by_user(person):
        for advertisement in advertisement_created_by_user(person):
            is_liked=False
            if checking_user_liked_ad(advertisement, person):
                is_liked = True
            returning_ad_created_by_user(advertisement, is_liked,my_advertisement_list)
    return {"data": {"message": my_advertisement_list}}, 200


def advertisement_created_by_user(person):
    return Advertisement.query.filter_by(user_id=person).order_by(Advertisement.created_at.desc()).all()


def checking_user_liked_ad(advertisement, person):
    return FavouriteAd.query.filter_by(ad_id=advertisement.id, user_id=person).first()


def returning_ad_created_by_user(advertisement, is_liked,my_advertisement_list):
    ad_images = AdImage.query.filter_by(ad_id=advertisement.id, is_cover_image=True).first()
    if os.getenv('ENV') == 'DEVELOPMENT':
        images = os.getenv('HOME_ROUTE') + ad_images.file
    if os.getenv('ENV') == 'PRODUCTION':
        images = app.config['S3_LOCATION'] + ad_images.file
    ad_filter = {"id": advertisement.id, "title": advertisement.title, "cover_image": images,
                 "featured": advertisement.is_featured, "location": advertisement.location,
                 "price": advertisement.price, "status": advertisement.status,
                 "favourite": is_liked, "disabled": advertisement.is_disabled}
    my_advertisement_list.append(ad_filter)


@ad.route("/my_favourite_ad", methods=["GET"])
@jwt_required()
def my_favourite_ads():
    person=get_jwt_identity()
    my_favourite_list=[]
    if user_favourite_ads(person):
        for favourite in user_favourite_ads(person):
            if not checking_for_disabled_ads(favourite):
                returning_my_favourites(favourite, my_favourite_list)
    return {"data": {"message": my_favourite_list}}, 200


def user_favourite_ads(person):
    return FavouriteAd.query.filter_by(user_id=person).order_by(FavouriteAd.created_at.desc()).all()


def favourite_advertisement(favourite):
    return Advertisement.query.filter(Advertisement.id==favourite.ad_id).first()


def checking_for_disabled_ads(favourite):
    return favourite_advertisement(favourite).is_disabled


def returning_my_favourites(favourite, my_favourite_list):
    ad_images = AdImage.query.filter_by(ad_id=favourite_advertisement(favourite).id, is_cover_image=True).first()
    if os.getenv('ENV') == 'DEVELOPMENT':
        images = os.getenv('HOME_ROUTE') + ad_images.file
    if os.getenv('ENV') == 'PRODUCTION':
        images = app.config['S3_LOCATION'] + ad_images.file
    ad_filter = {"id": favourite_advertisement(favourite).id, "title": favourite_advertisement(favourite).title,
                 "cover_image": images, "featured": favourite_advertisement(favourite).is_featured,
                 "location": favourite_advertisement(favourite).location,
                 "price": favourite_advertisement(favourite).price,
                 "status": favourite_advertisement(favourite).status, "favourite": True}
    my_favourite_list.append(ad_filter)


@ad.route("/report_ad/<int:ad_id>", methods=["POST"])
@jwt_required()
def report_ads(ad_id):
    person = get_jwt_identity()
    if filtering_ad_by_id(ad_id) is None:
        return {"data": {"error": "ad not found"}}, 400
    if checking_user_already_reported_ad(person, ad_id):
        return {"data": {"error": ErrorCodes.ad_already_reported_by_user.value['msg'],
                         "error_id": ErrorCodes.ad_already_reported_by_user.value['code']}}, 400
    return reporting_ad_and_checking_number_of_reports(person, ad_id)


def checking_user_already_reported_ad(person, ad_id):
    return ReportAd.query.filter(ReportAd.ad_id == ad_id, ReportAd.user_id == person).first()


def reporting_ad_and_checking_number_of_reports(person, ad_id):
    report_the_ad = ReportAd(user_id=person, ad_id=ad_id)
    db.session.add(report_the_ad)
    db.session.commit()
    if ReportAd.query.filter(ReportAd.ad_id == ad_id).count() >= app.config['COUNT_OF_REPORTS']:
        filtering_ad_by_id(ad_id).is_disabled = True
        db.session.add(filtering_ad_by_id(ad_id))
        db.session.commit()
    return {"data": {"message": "ad reported"}}, 200


@ad.route('/get_notification', methods=['GET'])
@jwt_required()
def get_notification():
    person = get_jwt_identity()
    notifications = Notification.query.filter(Notification.receiver_id == person).order_by(Notification.created_at.desc()).all()
    notification_list = []
    for notification in notifications:
        notification_dic = {"notify": notification.content, "created_time": notification.created_at, "is_read": notification.is_read}
        notification_list.append(notification_dic)
        notification.is_read = True
        db.session.add(notification)
        db.session.commit()
    return {"data": {'message': notification_list}}


# @socketio.on('connect', namespace='/notification')
# @jwt_required()
# def connect_handler():
#     person = get_jwt_identity()
#     user_room = 'user_{}'.format(person)
#     join_room(user_room)
#     emit('response', {'message': 'user connected'})


@ad.route('/create_room', methods=['GET'])
@jwt_required()
def create_room():
    person = get_jwt_identity()
    ad_id = request.args.get("ad_id")
    ad_owner = Advertisement.query.filter(Advertisement.id == ad_id).first().user_id
    checking_existing_room = Chatroom.query.filter(Chatroom.ad_id == ad_id, ((Chatroom.user_a == person) & (Chatroom.user_b == ad_owner)) | ((Chatroom.user_a == ad_owner) & (Chatroom.user_b == person))).first()
    if checking_existing_room:
        return {"data": {"message": {"room_name": checking_existing_room.chatroom, "room_id": checking_existing_room.id}}}
    person_username = User.query.filter(User.id == person).first().username
    ad_owner_username = User.query.filter(User.id == ad_owner).first().username
    chatroom = f'{ad_id}_{person_username}_{ad_owner_username}'
    chat_room = Chatroom(chatroom=chatroom, user_a=person, user_b=ad_owner, ad_id=ad_id)
    db.session.add(chat_room)
    db.session.commit()
    chatroom_details = Chatroom.query.filter(Chatroom.chatroom == chatroom).first()
    return {"data": {"message": {"room_name": chatroom_details.chatroom, "room_id": chatroom_details.id}}}


@ad.route('/list_all_messages_room', methods=['GET'])
@jwt_required()
def list_all_chats():
    person = get_jwt_identity()
    current_username = User.query.filter(User.id == person).first().username
    chat_rooms = Chatroom.query.filter(or_(Chatroom.user_a == person, Chatroom.user_b == person)).order_by(Chatroom.updated_at.desc()).all()
    chat_list = []
    for chatroom in chat_rooms:
        other_user = chatroom.user_a if chatroom.user_a != person else chatroom.user_b
        image = UserProfile.query.filter(UserProfile.user_id == other_user).first().photo
        ad_title = Advertisement.query.filter(Advertisement.id == chatroom.ad_id).first().title
        ad_image = AdImage.query.filter(AdImage.ad_id == chatroom.ad_id, AdImage.is_cover_image == True).first().file
        ad_image_url = os.getenv('HOME_ROUTE') + ad_image
        url = os.getenv('HOME_ROUTE') + image
        username_1 = User.query.filter(User.id == chatroom.user_a).first().username
        username_2 = User.query.filter(User.id == chatroom.user_b).first().username
        extracting_last_message = Message.query.filter(Message.chatroom_id == chatroom.id).order_by(Message.created_at.desc()).first()
        unread_message = Message.query.filter(Message.chatroom_id == chatroom.id, Message.receiver_id == person,
                                              Message.is_read == False).count()
        if not extracting_last_message:
            last_message = None
            time_last_message = None
            username_who_send_last_message = None
        else:
            last_message = extracting_last_message.content
            time_last_message = extracting_last_message.created_at
            username_who_send_last_message = User.query.filter(User.id == extracting_last_message.sender_id).first().username
        chat = {"photo": url, "time_last_message": time_last_message, "user_who_send_last_message": username_who_send_last_message,
                "chatroom_name": chatroom.chatroom,
                "ad_image_url": ad_image_url, "room_id": chatroom.id,
                "unread_message": unread_message,
                "last_message": last_message,
                "username_1": username_1, "username_2": username_2}
        chat_list.append(chat)
    return {"data": {"message": chat_list}}


@ad.route('/chat_messages', methods=['GET'])
@jwt_required()
def list_a_chat():
    person = get_jwt_identity()
    if "room_id" not in request.args:
        return {"data": {"error": "provide the room_id"}}, 400
    room_id = request.args.get("room_id")
    reading_unread_messages = Message.query.filter(Message.chatroom_id == room_id, Message.receiver_id == person,
                                                   Message.is_read == False).all()
    for message in reading_unread_messages:
        message.is_read = True
        db.session.add(message)
        db.session.commit()

    chatroom = Chatroom.query.filter(Chatroom.id == int(room_id)).first()
    messages = Message.query.filter(Message.chatroom_id == int(room_id)).order_by(Message.created_at.asc()).all()
    other_user_id = chatroom.user_a if chatroom.user_a != person else chatroom.user_b
    user_image = UserProfile.query.filter(UserProfile.user_id == other_user_id).first().photo
    other_username = User.query.filter(User.id == other_user_id).first().username
    ad_id = chatroom.ad_id
    ads = Advertisement.query.filter(Advertisement.id == ad_id).first()
    ad_title = ads.title
    ad_price = ads.price
    ad_image = AdImage.query.filter(AdImage.id == ad_id, AdImage.is_cover_image == True).first().file
    message_list = []
    for message in messages:
        each_message = message.content
        sender_name = User.query.filter(User.id == message.sender_id).first().username
        each_message_dict = {"sender_name": sender_name, "message": each_message}
        message_list.append(each_message_dict)
    return {"data": {"message": message_list}, "other_user": other_username, "user_image": user_image,
            "ads_image": ad_image, "ad_title": ad_title, "ad_price": ad_price}


@socketio.on('joined', namespace='/chat')
def joined(message):
    room = request.args.get("room_id")
    join_room(int(room))
    emit('status', {'message': f'User joined the room {room}'}, room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    room = request.args.get('room_id')
    leave_room(int(room))
    emit('status', {'message': f'User left the room {room}'})


@socketio.on('text', namespace='/chat')
def handle_send_message(data):
    person = get_jwt_identity()
    chatroom_id = data.get('chatroom_id')
    content = data.get('content')
    chatroom = Chatroom.query.filter(Chatroom.id == int(chatroom_id)).first()
    chatroom.updated_at = datetime.now
    db.session.add(chatroom)
    db.session.commit()
    other_user = chatroom.user_a if chatroom.user_a != person else chatroom.user_b
    message = Message(chatroom_id=chatroom.id, sender_id=person, receiver_id=other_user, content=content)
    db.session.add(message)
    db.session.commit()
    sender_name = User.query.filter(User.id == person).first().username
    receiver_name = User.query.filter(User.id == other_user).first().username
    emit('receive_message', {"receiver_name": receiver_name, 'chatroom_id': chatroom.id, "sender_name": sender_name,
                             'sender_id': person, 'content': content}, room=chatroom.chatroom)














































































































