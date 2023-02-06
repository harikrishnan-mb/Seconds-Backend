from flask import Blueprint,request
from s3config import s3
from advertisement.models import db, Category, Advertisement, AdImage, AdPlan, FavouriteAd, ReportAd
from user.api import check_email,check_phone
from user.models import User, UserProfile
from user.api import get_jwt_identity,jwt_required,verify_jwt_in_request
from geoalchemy2 import WKTElement
from messages import ErrorCodes
import os
from datetime import datetime, timedelta
import secrets
import string
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, or_, and_,union
from werkzeug.utils import secure_filename
from createapp import get_app
from dotenv import load_dotenv
load_dotenv()
app = get_app()
ad=Blueprint('ad',__name__)
engine=create_engine(os.getenv("ENGINE"))

@ad.route("/list_every_category", methods=["GET"])
def list_every_category():
    categories_list = []
    return get_every_categories(categories_list)
def get_every_categories(categories_list):
    for category in filtering_main_category():
        sub_categories_list = []
        sub_categories = Category.query.filter_by(parent_id=category.id).all()
        for sub_category in sub_categories:
            sub_category_name = {"id": sub_category.id, "name": sub_category.name}
            sub_categories_list.append(sub_category_name)
        if os.getenv('ENV') == 'DEVELOPMENT':
            category_name = {"id": category.id, "name": category.name, "images": os.getenv("HOME_ROUTE")+category.image, "sub_category": sub_categories_list}
        if os.getenv('ENV')=='PRODUCTION':
            category_name = {"id": category.id, "name": category.name,"images": app.config['S3_LOCATION'] + category.image, "sub_category": sub_categories_list}
        categories_list.append(category_name)
    return {"data": {"message": categories_list}}, 200

def filtering_main_category():
    return Category.query.filter_by(parent_id=None).order_by(Category.id).all()

@ad.route("/category", methods=["GET"])
def list_category():
    categories_list = []
    return get_only_categories(categories_list)

def get_only_categories(categories_list):
    for category in filtering_main_category():
        if os.getenv('ENV') == 'DEVELOPMENT':
            category_name = {"id":category.id, "name": category.name, "images": os.getenv("HOME_ROUTE")+category.image}
        if os.getenv('ENV') == 'PRODUCTION':
            category_name = {"id": category.id, "name": category.name, "images": app.config['S3_LOCATION'] + category.image}
        categories_list.append(category_name)
    return{"data": {"message": categories_list}}, 200


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

def admin_is_true(person):
    return User.query.filter_by(id=person).first().is_admin

def deleting_the_category(category_id):
    db.session.delete(filtering_category(category_id))
    db.session.commit()
    return {"data": {"message": "category removed"}}, 200

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
                return {"data":{"error":"parent_id should be integer"}}, 400
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
                    s3.upload_fileobj(file, app.config['S3_BUCKET'], 'static/catagory/' + filename, ExtraArgs={"ACL": "public-read","ContentType": file.content_type})
                category_add = Category(name=category, image='static/catagory/' + filename, parent_id=None)
        return adding_category_to_db(category_add)
    else:
        return {"data": {"error": "only admin can add category"}}, 400

def checking_category_name_already_exist(category):
    return Category.query.filter_by(name=category).first()

def checking_parent_id_exist(parent_id):
    return Category.query.filter_by(id=parent_id).first()

def adding_category_to_db(category_add):
    db.session.add(category_add)
    db.session.commit()
    return {"data": {"message": "Category created"}}, 200

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
                return {"data": {"error": "provide category name"}}
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
                    parent_id=float(parent_id)
                except ValueError:
                    return {"data":{"error":"parent_id should be integer"}}, 400
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
                    if os.getenv("ENV")=="DEVELOPMENT":
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

def checking_new_and_old_category_name_not_same(category_id, category):
    return filtering_category(category_id).name!=category
def filtering_category(category_id):
     return Category.query.filter_by(id=category_id).first()
def updating_category_in_db(category_id):
    db.session.add(filtering_category(category_id))
    db.session.commit()
    return {"data": {"message": "Category updated"}}, 200

@ad.route("/ad_plan", methods=["GET"])
def list_ad_plan():
    ad_plan_list = []
    return ads_plan(ad_plan_list)

def ads_plan(ad_plan_list):
    ad_plans = AdPlan.query.all()
    for ad_plan in ad_plans:
        ad_plan_name = {"id": ad_plan.id, "price": ad_plan.price, "days": ad_plan.days}
        ad_plan_list.append(ad_plan_name)
    return {"data": {"message": ad_plan_list}}, 200


def allowed_img_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png','jpg','jpeg','webp'}

def generate_random_text():
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(14))


@ad.route("/delete_ad/<int:del_ad_id>", methods=["DELETE"])
@jwt_required()
def delete_ad(del_ad_id):
    person = get_jwt_identity()
    if filtering_ad_by_id(del_ad_id) is None:
        return {"data": {"error": "ad not found"}}
    if checking_user_posted_ad(del_ad_id, person):
        return deleting_ad(del_ad_id)
    return {"data": {"error": "invalid request"}}

def checking_user_posted_ad(del_ad_id, person):
    return filtering_ad_by_id(del_ad_id).user_id == person

def filtering_ad_by_id(del_ad_id):
    return Advertisement.query.filter_by(id=del_ad_id).first()

def deleting_ad(del_ad_id):
    filtering_ad_by_id(del_ad_id).is_deleted = True
    db.session.add(filtering_ad_by_id(del_ad_id))
    db.session.commit()
    return {"data": {"message": "ad deleted"}}, 200

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
        return {"data": {"error": "provide category id as integer"}},400
    if checking_category_id_exist(category_id) is None:
        return {"data": {"error": "category id not found"}}, 400
    if not images:
        return {"data":{"error": ErrorCodes.image_field_is_required.value['msg'], 'error_id': ErrorCodes.image_field_is_required.value['code']}}, 400
    for image in images:
        if not image:
            return {"data": {"error": "provide image"}}, 400
        if image and not allowed_img_file(image.filename):
            return {"data":{"error": ErrorCodes.image_should_be_in_png_webp_jpg_or_jpeg_format.value['msg'], "error_id": ErrorCodes.image_should_be_in_png_webp_jpg_or_jpeg_format.value['code']}}, 400
    if not title:
        return {"data": {"error": "provide title"}}, 400
    if not status:
        status='active'
    if not seller_type:
        return {"data": {"error": "provide seller_type"}}, 400
    if not description:
        description=''
    if not price:
        return {"data": {"error": "provide price"}}, 400
    try:
        price = float(price)
    except ValueError:
        return {"data": {"error": "provide price as floating number"}}, 400
    if not negotiable_product:
        return {"data": {"error": "provide product is negotiable or not"}}, 400
    if negotiable_product.capitalize()=="True":
        negotiable_product=True
    elif negotiable_product.capitalize()=="False":
        negotiable_product=False
    else:
        return {"data": {"error": "provide product is negotiable or not as True or False"}}, 400
    if not feature_product:
        return {"data": {"error": "provide product is featured or not"}}, 400
    if feature_product.capitalize()=="True":
        feature_product=True
        if not ad_plan_id:
            return {"data": {"error": "provide advertisement plan id"}}, 400
        try:
            ad_plan_id = int(ad_plan_id)
        except ValueError:
            return {"data": {"error": "provide advertisement plan id as integer"}}, 400
        if not checking_adplan_exist(ad_plan_id):
            return {"data": {"error": "advertisement plan id not found"}}, 400
    elif feature_product.capitalize()=="False":
        feature_product=False
        ad_plan_id=None
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
        return {"data":{"error": "provide phone number"}}, 400
    if not check_phone(phone):
        return {"data": {"error": "provide valid phone number"}}, 400
    if not email_id:
        email_id=''
    if email_id and not check_email(email_id):
        return {"data": {"error": "provide valid email"}}, 400
    geo = WKTElement('POINT({} {})'.format(str(longitude), str(latitude)))

    return saving_created_ad(title,person,description,category_id,status,seller_type,price,ad_plan_id,negotiable_product,feature_product,location,latitude,longitude,seller_name,phone,email_id, images, geo)

def saving_created_ad(title,person,description,category_id,status,seller_type,price,ad_plan_id,negotiable_product,feature_product,location,latitude,longitude,seller_name,phone,email_id, images, geo):
    with Session(engine) as session:
        session.begin()
        try:
            ad_1 = Advertisement(title=title, user_id=get_jwt_identity(),
                                 description=description, category_id=category_id,
                                 status=status, seller_type=seller_type,
                                 price=price, advertising_plan_id=ad_plan_id, is_deleted=False,
                                 is_negotiable=negotiable_product, is_featured=feature_product,
                                 location=location, latitude=latitude, longitude=longitude,
                                 seller_name=seller_name, phone=phone, email=email_id,
                                 advertising_id=generate_random_text(), geo=geo)
            session.add(ad_1)
            for image in images:
                display_order = images.index(image) + 1
                if images.index(image) == 0:
                    cover_image = True
                else:
                    cover_image = False
                filename = ad_1.advertising_id+secure_filename(image.filename)
                if os.getenv('ENV')=='DEVELOPMENT':
                    image.save(os.path.join(app.config['UPLOAD_AD_PICTURE'], filename))
                if os.getenv('ENV')=='PRODUCTION':
                    s3.upload_fileobj(image, app.config['S3_BUCKET'],'static/images_ad/' + filename,
                        ExtraArgs={"ACL": "public-read", "ContentType": image.content_type})
                session.commit()
                ad_image_1 = AdImage(display_order=display_order, file='static/images_ad/' + filename,
                                     is_cover_image=cover_image, ad_id=ad_1.id)
                session.add(ad_image_1)
        except:
            session.rollback()
            session.close()
            return {"data": {"error": "error uploading image"}}, 400
        else:
            session.commit()
            return {"data": {"message": "ad created"}}, 200


def checking_category_id_exist(category_id):
    return Category.query.filter_by(id=int(category_id)).first()


def checking_adplan_exist(ad_plan_id):
    return AdPlan.query.filter_by(id=ad_plan_id).first()


@ad.route("/view_ad", methods=["GET"], defaults={"page": 1})
@ad.route("/view_ad/<int:page>", methods=["GET"])
def view_ad(page):
    sorts = [Advertisement.is_featured.desc() ]
    filter_list = [Advertisement.status == "active", Advertisement.is_deleted == False, Advertisement.is_disabled == False]
    count_list = [Advertisement.status == "active", Advertisement.is_deleted == False, Advertisement.is_disabled == False]

    #filtering based on min_price, max_price, main_category_id and subcategory_id
    if "max_price" in request.args:
        max_price = request.args["max_price"]
        price=Advertisement.price <= max_price
        filter_list.append(price)
    if "min_price" in request.args:
        min_price = request.args["min_price"]
        price=Advertisement.price >= min_price
        filter_list.append(price)
    if "category_id" in request.args:
        category_id = request.args["category_id"]
        category_id=category_id.split(',')
        category_map=map(int,category_id)
        category_id_list=list(category_map)
        cat_id=Advertisement.category_id.in_(category_id_list)
        filter_list.append(cat_id)
    if "main_category_id" in request.args:
        main_category_id = request.args["main_category_id"]
        main_category_id=main_category_id.split(',')
        main_category_map=map(int,main_category_id)
        categories_list=list(main_category_map)
        sub_category_list=[]
        for category_id in categories_list:
            sub_categories=Category.query.filter_by(parent_id=category_id).all()
            for sub_category in sub_categories:
                sub_category_list.append(sub_category.id)
        category_ids=Advertisement.category_id.in_(sub_category_list)
        filter_list.append(category_ids)
        count_list.append(category_ids)

    # sorting based on time, price: high to low and price: low to high
    if "sort" in request.args:
        sort = request.args["sort"]
        if sort=="time":
            sort_1 = Advertisement.created_at.desc()
            sorts.append(sort_1)
        if sort=="hightolow":
            sort_1=Advertisement.price.desc()
            sorts.append(sort_1)
        if sort=="lowtohigh":
            sort_1=Advertisement.price.asc()
            sorts.append(sort_1)
    if "sort" not in request.args:
        sorts.append(Advertisement.created_at.desc())

    #location based filtering
    if "lat" and "long" in request.args:
        lat=request.args["lat"]
        long=request.args["long"]
        loc_point=WKTElement('POINT({} {})'.format(str(long), str(lat)))
        loc_radius=20000
        query=(func.ST_Distance(Advertisement.geo, loc_point) < loc_radius)
        filter_list.append(query)
        count_list.append(query)

    #searching
    if "search" in request.args:
        search = request.args["search"]
        search_lists=search.split(' ')
        searching_the_ad(search_lists,filter_list,count_list)

    list_ad = []
    return listing_the_ad(filter_list,sorts,list_ad,page,count_list)

def searching_the_ad(search_lists,filter_list,count_list):
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
            search_query=None
        filter_list.append(search_query)
        count_list.append(search_query)
    return filter_list, count_list


def listing_the_ad(filter_list,sorts,list_ad,page,count_list):
    adv=Advertisement.query.filter_by(is_featured=True).all()
    for ads in adv:
        plan=AdPlan.query.filter_by(id=ads.advertising_plan_id).first()
        if datetime.now()-ads.created_at>timedelta(days=plan.days):
            ads.is_featured=False
            db.session.add(ads)
            db.session.commit()
    count_of_price_range_0_to_1_lakh = Advertisement.query.filter(*count_list,and_(Advertisement.price>=0, Advertisement.price<100000)).count()
    count_of_price_range_1_to_3_lakh = Advertisement.query.filter(*count_list, and_(Advertisement.price >= 100000,Advertisement.price < 300000)).count()
    count_of_price_range_3_to_6_lakh = Advertisement.query.filter(*count_list, and_(Advertisement.price >= 300000, Advertisement.price < 600000)).count()
    count_of_price_range_greater_than_6_lakh = Advertisement.query.filter(*count_list, and_(Advertisement.price >= 600000)).count()
    advertisements = Advertisement.query.filter(*filter_list).order_by(*sorts).paginate(page=page,per_page=12,error_out=False)
    number_of_ads=Advertisement.query.filter(*filter_list).count()
    for advertisement in advertisements:
        is_liked=False
        if "Authorization" in request.headers:
            verify_jwt_in_request()
            person=get_jwt_identity()
            if FavouriteAd.query.filter_by(ad_id=advertisement.id, user_id=person).first():
                is_liked=True
        ad_images = AdImage.query.filter_by(ad_id=advertisement.id, is_cover_image=True).first()
        if os.getenv('ENV')=='DEVELOPMENT':
            images=os.getenv('HOME_ROUTE') + ad_images.file
        if os.getenv('ENV')=='PRODUCTION':
            images=app.config['S3_LOCATION'] + ad_images.file
        ad_filter = {"id": advertisement.id, "title": advertisement.title, "cover_image": images, "featured": advertisement.is_featured,
                     "location": advertisement.location, "price": advertisement.price, "status":advertisement.status, "favourite": is_liked}
        list_ad.append(ad_filter)
    return {"data": {"message": list_ad, "count": number_of_ads, "below_one_lakh": count_of_price_range_0_to_1_lakh, "one_to_three_lakh": count_of_price_range_1_to_3_lakh,
                     "three_to_six_lakh": count_of_price_range_3_to_6_lakh,"above_six_lakh": count_of_price_range_greater_than_6_lakh}}, 200

@ad.route("/update_ad/<int:ads_id>", methods=["PUT"])
@jwt_required()
def update_ad(ads_id):
    person = get_jwt_identity()
    if checking_user_posted_ad(ads_id,person):
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
        if not images:
            return {"data": {"error": ErrorCodes.image_field_is_required.value['msg'], 'error_id': ErrorCodes.image_field_is_required.value['code']}}, 400
        for image in images:
            if image.filename == '':
                return {"data":{"error": "provide image"}}, 400
            if image and not allowed_img_file(image.filename):
                return {"data":{"error": ErrorCodes.image_should_be_in_png_webp_jpg_or_jpeg_format.value['msg'],"error_id": ErrorCodes.image_should_be_in_png_webp_jpg_or_jpeg_format.value['code']}}, 400
        try:
            category_id=int(category_id)
        except ValueError:
            return {"data": {"error": "provide category id as integer"}}, 400
        if checking_category_id_exist(category_id) is None:
            return {"data": {"error": "category id not found"}}, 400
        if not title:
            return {"data": {"error": "provide title"}}, 400
        if not status:
            status='active'
        if not seller_type:
            return {"data": {"error": "provide seller_type"}}, 400
        if not description:
            description=''
        if not price:
            return {"data": {"error": "provide price"}}, 400
        try:
            price = float(price)
        except ValueError:
            return {"data": {"error": "provide price as floating number"}}, 400
        if not negotiable_product:
            return {"data": {"error": "provide product is negotiable or not"}}, 400
        if negotiable_product.capitalize()=="True":
            negotiable_product=True
        elif negotiable_product.capitalize()=="False":
            negotiable_product=False
        else:
            return {"data": {"error": "provide product is negotiable or not as True or False"}}, 400
        if not feature_product:
            return {"data": {"error": "provide product is featured or not"}}, 400
        if feature_product.capitalize()=="True":
            feature_product=True
            if not ad_plan_id:
                return {"data": {"error": "provide advertisement plan id"}}, 400
            try:
                ad_plan_id = int(ad_plan_id)
            except ValueError:
                return {"data": {"error": "provide advertisement plan id as integer"}}, 400
            if not checking_adplan_exist(ad_plan_id):
                return {"data": {"error": "advertisement plan id not found"}}, 400
        elif feature_product.capitalize()=="False":
            feature_product=False
            ad_plan_id=None
        else:
            return {"data": {"error": "provide product is featured or not as True or False"}}, 400
        if not location:
            return {"data": {"error": "provide location"}}, 400
        if not latitude:
            return {"data": {"error": "provide latitude"}},400
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
        if  float(longitude) is False:
            return {"data": {"error": "provide longitude as floating number"}}, 400
        if not seller_name:
            return {"data": {"error": "provide seller_name"}}, 400
        if not phone:
            return {"data":{"error": "provide phone number"}}, 400
        if not check_phone(phone):
            return {"data": {"error": "provide valid phone number"}}, 400
        if not email_id:
            email_id=''
        if email_id and not check_email(email_id):
            return {"data": {"error": "provide valid email"}}, 400
        geo = WKTElement('POINT({} {})'.format(str(longitude), str(latitude)))
        return updating_ad_details(title,person,description,category_id,status,seller_type,price,ad_plan_id,negotiable_product,feature_product,location,latitude,longitude,seller_name,phone,email_id, images, ads_id, geo)
    else:
        return{"data": {"error": "only owner can edit ad"}}, 400

def updating_ad_details(title,person,description,category_id,status,seller_type,price,ad_plan_id,negotiable_product,feature_product,location,latitude,longitude,seller_name,phone,email_id, images, ads_id, geo):
    try:
        adv = Advertisement.query.filter_by(id=ads_id).first()
        adv.title = title
        adv.description = description
        adv.category_id = category_id
        adv.status = status
        adv.seller_type = seller_type
        adv.price = price
        adv.advertising_plan_id = ad_plan_id
        adv.is_negotiable = negotiable_product
        adv.is_featured = feature_product
        adv.location = location
        adv.latitude = latitude
        adv.longitude = longitude
        adv.seller_name = seller_name
        adv.phone = phone
        adv.email = email_id
        adv.geo = geo
        adv.updated_at=datetime.now()
        ad_images = AdImage.query.filter_by(ad_id=ads_id).all()
        for ad_image in ad_images:
            db.session.delete(ad_image)
        for image in images:
            display_order = images.index(image) + 1
            if images.index(image) == 0:
                cover_image = True
            else:
                cover_image = False
            filename = adv.advertising_id + secure_filename(image.filename)
            if os.getenv('ENV') == 'DEVELOPMENT':
                image.save(os.path.join(app.config['UPLOAD_AD_PICTURE'], filename))
            if os.getenv('ENV') == 'PRODUCTION':
                s3.upload_fileobj(image, app.config['S3_BUCKET'],'static/images_ad/' + filename, ExtraArgs={"ACL": "public-read", "ContentType": image.content_type})
            ad_image_1 = AdImage(display_order=display_order, file='static/images_ad/' + filename, is_cover_image=cover_image, ad_id=adv.id)
            db.session.add(ad_image_1)
        db.session.commit()
        return {"data": {"message": "ad edited successfully"}}, 200
    except:
        return {"data": {"error": "error uploading image"}}, 400

@ad.route("/ad_details/<int:ad_id>", methods=["GET"])
def details_of_ad(ad_id):
    if filtering_ad_by_id(ad_id) is None:
        return {"data": {"error": "ad not found"}}, 400
    image_list=[]
    is_liked = False
    if "Authorization" in request.headers:
        verify_jwt_in_request()
        person = get_jwt_identity()
        if FavouriteAd.query.filter_by(ad_id=ad_id, user_id=person).first():
            is_liked = True
    return returning_ad_detail(image_list,ad_id,is_liked)

def filtering_user_created_ad(ad_id):
    return UserProfile.query.filter_by(user_id=filtering_ad_by_id(ad_id).user_id).first()

def filtering_image_of_ad(ad_id):
    return AdImage.query.filter_by(ad_id=ad_id).all()

def filtering_category_name_of_ad(ad_id):
    sub_category=Category.query.filter_by(id=filtering_ad_by_id(ad_id).category_id).first()
    return Category.query.filter_by(id=sub_category.parent_id).first().name

def returning_ad_detail(image_list,ad_id,is_liked):
    for ad_image in filtering_image_of_ad(ad_id):
        if os.getenv('ENV')=='DEVELOPMENT':
            image_list.append(os.getenv('HOME_ROUTE')+ad_image.file)
        if os.getenv('ENV') == 'PRODUCTION':
            image_list.append(app.config['S3_LOCATION'] + ad_image.file)
    if os.getenv('ENV') == 'DEVELOPMENT':
        images = os.getenv('HOME_ROUTE') + filtering_user_created_ad(ad_id).photo
    if os.getenv('ENV') == 'PRODUCTION':
        images = app.config['S3_LOCATION'] + filtering_user_created_ad(ad_id).photo
    return {"id": filtering_ad_by_id(ad_id).id, "title": filtering_ad_by_id(ad_id).title, "description":filtering_ad_by_id(ad_id).description, "advertising_id":filtering_ad_by_id(ad_id).advertising_id, "images": image_list, "seller_name":filtering_ad_by_id(ad_id).seller_name, "featured": filtering_ad_by_id(ad_id).is_featured,
            "latitude":filtering_ad_by_id(ad_id).latitude,"longitude":filtering_ad_by_id(ad_id).longitude, "location": filtering_ad_by_id(ad_id).location, "price": filtering_ad_by_id(ad_id).price, "posted_at": filtering_ad_by_id(ad_id).created_at, "photo": images, "status":filtering_ad_by_id(ad_id).status, "favourite": is_liked, "category_name": filtering_category_name_of_ad(ad_id)}, 200


@ad.route("/similar_ads/<int:ad_id>", methods=["GET"],defaults={"page": 1})
@ad.route("/similar_ads/<int:ad_id>/<int:page>", methods=["GET"])
def recommended_ad(ad_id,page):
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

def splitting_title(ad_id,sorts):
    sorts_query = func.ST_Distance(Advertisement.geo, filtering_ad_by_id(ad_id).geo).asc()
    sorts.append(sorts_query)
    return filtering_ad_by_id(ad_id).title

def searching_in_title_list(titles_list, search_list):
    for title in titles_list:
        if Advertisement.query.filter(func.lower(Advertisement.title).contains(func.lower(title))).first():
            filters=func.lower(Advertisement.title).contains(func.lower(title))
            search_list.append(filters)
        else:
            search_list=search_list
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
                 "location": advertisement.location, "price": advertisement.price, "status": advertisement.status,
                 "favourite": is_liked}
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
    person=get_jwt_identity()
    if filtering_ad_by_id(ad_id) is None:
        return {"data": {"error": "ad not found"}}, 400
    if checking_user_favourited_ad(person, ad_id):
        return removing_ad_from_favourite(person, ad_id)
    favourite = FavouriteAd(ad_id=ad_id, user_id=person)
    return saving_ad_to_favourite(favourite)
def checking_user_favourited_ad(person, ad_id):
    return FavouriteAd.query.filter_by(ad_id=ad_id, user_id=person).first()

def removing_ad_from_favourite(person, ad_id):
    db.session.delete(checking_user_favourited_ad(person, ad_id))
    db.session.commit()
    return {"data": {"message": "ad removed from favourites"}}, 200

def saving_ad_to_favourite(favourite):
    db.session.add(favourite)
    db.session.commit()
    return {"data": {"message": "ad saved to favourites"}}, 200

@ad.route("/view_my_ads", methods=["GET"])
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
    ad_filter = {"id": advertisement.id, "title": advertisement.title, "cover_image": images, "featured": advertisement.is_featured,
                 "location": advertisement.location, "price": advertisement.price, "status": advertisement.status, "favourite": is_liked,
                 "disabled": advertisement.is_disabled}
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
    ad_filter = {"id": favourite_advertisement(favourite).id, "title": favourite_advertisement(favourite).title, "cover_image": images,"featured": favourite_advertisement(favourite).is_featured,
                 "location": favourite_advertisement(favourite).location, "price": favourite_advertisement(favourite).price, "status": favourite_advertisement(favourite).status, "favourite": True}
    my_favourite_list.append(ad_filter)

@ad.route("/report_ad/<int:ad_id>", methods=["POST"])
@jwt_required()
def report_ads(ad_id):
    person = get_jwt_identity()
    if filtering_ad_by_id(ad_id) is None:
        return {"data": {"error": "ad not found"}}, 400
    if checking_user_already_reported_ad(person, ad_id):
        return {"data": {"error": "ad already reported by user"}}, 409
    return reporting_ad_and_checking_number_of_reports(person, ad_id)

def checking_user_already_reported_ad(person, ad_id):
    return ReportAd.query.filter(ReportAd.ad_id == ad_id, ReportAd.user_id == person).first()

def reporting_ad_and_checking_number_of_reports(person, ad_id):
    report_the_ad = ReportAd(user_id=person, ad_id=ad_id)
    db.session.add(report_the_ad)
    db.session.commit()
    if ReportAd.query.filter(ReportAd.ad_id == ad_id).count() >= app.config['COUNT_OF_REPORTS']:
        advertisement = Advertisement.query.filter_by(id=ad_id).first()
        advertisement.is_disabled = True
        db.session.add(advertisement)
        db.session.commit()
    return {"data": {"message": "ad reported"}}, 200


















































































































