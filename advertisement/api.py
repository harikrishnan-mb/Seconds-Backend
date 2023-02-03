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
from sqlalchemy import create_engine, func, or_, and_
from werkzeug.utils import secure_filename
from createapp import get_app
from dotenv import load_dotenv
load_dotenv()
app = get_app()
ad=Blueprint('ad',__name__)
engine=create_engine(os.getenv("ENGINE"))

@ad.route("/list_every_category", methods=["GET"])
def list_every_category():
    return get_every_categories()
def get_every_categories():
    categories = Category.query.filter_by(parent_id=None).order_by(Category.id).all()
    categories_list = []
    for category in categories:
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

@ad.route("/category", methods=["GET"])
def list_category():
    return get_only_categories()
def get_only_categories():
    categories=Category.query.filter_by(parent_id=None).order_by(Category.id).all()
    categories_list=[]
    for category in categories:
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
    filter_user = User.query.filter_by(id=person).first()
    return filter_user.is_admin

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
                    s3.upload_fileobj(file, app.config['S3_BUCKET'], 'static/catagory/' + filename,
                        ExtraArgs={"ACL": "public-read","ContentType": file.content_type})
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
    return ads_plan()

def ads_plan():
    ad_plans = AdPlan.query.all()
    ad_plan_list = []
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
    filter_advertisement = Advertisement.query.filter_by(id=del_ad_id).first()
    return filter_advertisement

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
                    s3.upload_fileobj(
                        image,
                        app.config['S3_BUCKET'],
                        'static/images_ad/' + filename,
                        ExtraArgs={
                            "ACL": "public-read",
                            "ContentType": image.content_type
                        }
                    )
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
    category=Category.query.filter_by(id=int(category_id)).first()
    return category

def checking_adplan_exist(ad_plan_id):
    plan=AdPlan.query.filter_by(id=ad_plan_id).first()
    return plan

@ad.route("/view_ad", methods=["GET"], defaults={"page": 1})
@ad.route("/view_ad/<int:page>", methods=["GET"])
def view_ad(page):
    sorts=[Advertisement.is_featured.desc() ]
    filter_list= [Advertisement.status=="active", Advertisement.is_deleted==False, Advertisement.is_disabled==False]

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

    #location based filtering
    if "lat" and "long" in request.args:
        lat=request.args["lat"]
        long=request.args["long"]
        loc_point=WKTElement('POINT({} {})'.format(str(long), str(lat)))
        loc_radius=20000
        query=(func.ST_Distance(Advertisement.geo, loc_point) < loc_radius)
        filter_list.append(query)

    #searching
    if "search" in request.args:
        search = request.args["search"]
        search_lists=search.split(' ')
        searching_the_ad(search_lists,filter_list)

    list_ad = []
    return listing_the_ad(filter_list,sorts,list_ad, page)

def searching_the_ad(search_lists,filter_list):
    for search_list in search_lists:
        categories = Category.query.filter(func.lower(Category.name).contains(func.lower(search_list))).first()
        if not categories:
            ads = Advertisement.query.filter(func.lower(Advertisement.title).contains(func.lower(search_list))).first()
            if ads:
                search_query = func.lower(Advertisement.title).contains(func.lower(search_list))
            else:
                search_query = None
        else:
            search_query = Advertisement.category_id == categories.id
        filter_list.append(search_query)
    return filter_list


def listing_the_ad(filter_list,sorts,list_ad, page):
    adv=Advertisement.query.filter_by(is_featured=True).all()
    for ads in adv:
        plan=AdPlan.query.filter_by(id=ads.advertising_plan_id).first()
        if datetime.now()-ads.created_at>timedelta(days=plan.days):
            ads.is_featured=False
            db.session.add(ads)
            db.session.commit()
    count_of_price_range_0_to_1_lakh = Advertisement.query.filter(*filter_list,and_(Advertisement.price>=0, Advertisement.price<100000)).count()
    count_of_price_range_1_to_3_lakh = Advertisement.query.filter(*filter_list, and_(Advertisement.price >= 100000,Advertisement.price < 300000)).count()
    count_of_price_range_3_to_6_lakh = Advertisement.query.filter(*filter_list, and_(Advertisement.price >= 300000, Advertisement.price < 600000)).count()
    count_of_price_range_greater_than_6_lakh = Advertisement.query.filter(*filter_list, and_(Advertisement.price >= 600000)).count()
    advertisements = Advertisement.query.filter(*filter_list).order_by(*sorts).paginate(page=page,per_page=12,error_out=False)
    number_of_ads=Advertisement.query.filter(*filter_list).order_by(*sorts).count()
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
        ad_filter = {"id": advertisement.id, "title": advertisement.title,
                     "cover_image": images, "featured": advertisement.is_featured,
                     "location": advertisement.location, "price": advertisement.price, "status":advertisement.status, "favourite": is_liked}
        list_ad.append(ad_filter)
    return {"data": {"message": list_ad, "count": number_of_ads,
                     "below_one_lakh": count_of_price_range_0_to_1_lakh, "one_to_three_lakh": count_of_price_range_1_to_3_lakh,
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
        adv.updated_at=datetime.utcnow()
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
                s3.upload_fileobj(
                    image,
                    app.config['S3_BUCKET'],
                    'static/images_ad/' + filename,
                    ExtraArgs={
                        "ACL": "public-read",
                        "ContentType": image.content_type
                    }
                )
            ad_image_1 = AdImage(display_order=display_order, file='static/images_ad/' + filename,
                                 is_cover_image=cover_image, ad_id=adv.id)
            db.session.add(ad_image_1)
        db.session.commit()
        return {"data": {"message": "ad edited successfully"}}, 200
    except:
        return {"data": {"error": "error uploading image"}}, 400

@ad.route("/ad_details/<int:ad_id>", methods=["GET"])
def details_of_ad(ad_id):
    ads= Advertisement.query.filter_by(id=ad_id).first()
    ad_images=AdImage.query.filter_by(ad_id=ad_id).all()
    owner_ad = UserProfile.query.filter_by(user_id=ads.user_id).first()
    sub_category_name=Category.query.filter_by(id=ads.category_id).first().name
    image_list=[]
    is_liked = False
    if "Authorization" in request.headers:
        verify_jwt_in_request()
        person = get_jwt_identity()
        if FavouriteAd.query.filter_by(ad_id=ad_id, user_id=person).first():
            is_liked = True
    for ad_image in ad_images:
        if os.getenv('ENV')=='DEVELOPMENT':
            image_list.append(os.getenv('HOME_ROUTE')+ad_image.file)
        if os.getenv('ENV') == 'PRODUCTION':
            image_list.append(app.config['S3_LOCATION'] + ad_image.file)
    if os.getenv('ENV') == 'DEVELOPMENT':
        images = os.getenv('HOME_ROUTE') + owner_ad.photo
    if os.getenv('ENV') == 'PRODUCTION':
        images = app.config['S3_LOCATION'] + owner_ad.photo
    return {"id": ads.id, "title": ads.title, "description":ads.description, "advertising_id":ads.advertising_id, "images": image_list, "seller_name":ads.seller_name, "featured": ads.is_featured,
            "latitude":ads.latitude,"longitude":ads.longitude, "location": ads.location, "price": ads.price, "posted_at": ads.created_at, "photo": images, "status":ads.status, "favourite": is_liked,
            "sub_category_name": sub_category_name}

@ad.route("/similar_ads/<int:ad_id>", methods=["GET"],defaults={"page": 1})
@ad.route("/similar_ads/<int:ad_id>/<int:page>", methods=["GET"])
def recommended_ad(ad_id,page):
    ads = Advertisement.query.filter_by(id=ad_id).first()
    if ads is None:
        return {"data": {"error": "provide valid advertisement id"}}, 200
    sorts = [Advertisement.is_featured.desc()]
    filter_list = [Advertisement.status == "active", Advertisement.is_deleted == False, Advertisement.is_disabled == False, Advertisement.id!=ad_id]
    sorts_query = func.ST_Distance(Advertisement.geo, ads.geo).asc()
    sorts.append(sorts_query)
    ad_title = ads.title
    titles_list=ad_title.split(' ')
    search_list=[]
    for title in titles_list:
        if Advertisement.query.filter(func.lower(Advertisement.title).contains(func.lower(title))).first():
            filters=func.lower(Advertisement.title).contains(func.lower(title))
            search_list.append(filters)
        else:
            search_list=search_list
    category_ids = Advertisement.category_id==ads.category_id
    search_list.append(category_ids)
    filter_list.append(or_(*search_list))
    advertisements = Advertisement.query.filter(*filter_list).order_by(*sorts).paginate(page=page,per_page=10,error_out=False)
    list_recommended_ad=[]
    for advertisement in advertisements:
        is_liked = False
        if "Authorization" in request.headers:
            verify_jwt_in_request()
            person = get_jwt_identity()
            if person:
                if FavouriteAd.query.filter_by(ad_id=advertisement.id, user_id=person).first():
                    is_liked = True
        ad_images = AdImage.query.filter_by(ad_id=advertisement.id, is_cover_image=True).first()
        if os.getenv('ENV')=='DEVELOPMENT':
            images=os.getenv('HOME_ROUTE') + ad_images.file
        if os.getenv('ENV')=='PRODUCTION':
            images=app.config['S3_LOCATION'] + ad_images.file
        ad_filter = {"id": advertisement.id, "title": advertisement.title,
                     "cover_image": images, "featured": advertisement.is_featured,
                     "location": advertisement.location, "price": advertisement.price, "status":advertisement.status, "favourite": is_liked}
        list_recommended_ad.append(ad_filter)
    return {"data": {"message": list_recommended_ad }}

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

@ad.route("/favourite_ad/<int:ad_id>", methods=["GET"])
@jwt_required()
def favourite_ad(ad_id):
    person=get_jwt_identity()
    if filtering_ad_by_id(ad_id) is None:
        return {"data": {"error": "ad not found"}}, 400
    favourites=FavouriteAd.query.filter_by(ad_id=ad_id, user_id=person).first()
    if favourites:
        db.session.delete(favourites)
        db.session.commit()
        return {"data": {"message": "ad removed from favourites"}}, 200
    favourite = FavouriteAd(ad_id=ad_id, user_id=person)
    db.session.add(favourite)
    db.session.commit()
    return {"data": {"message": "ad saved to favourites"}}, 200

@ad.route("/view_my_ads", methods=["GET"])
@jwt_required()
def getting_my_ads():
    person=get_jwt_identity()
    advertisements=Advertisement.query.filter_by(user_id=person).order_by(Advertisement.created_at.desc()).all()
    my_advertisement_list=[]
    if advertisements:
        for advertisement in advertisements:
            is_liked=False
            if FavouriteAd.query.filter_by(ad_id=advertisement.id, user_id=person).first():
                is_liked = True
            ad_images = AdImage.query.filter_by(ad_id=advertisement.id, is_cover_image=True).first()
            if os.getenv('ENV') == 'DEVELOPMENT':
                images = os.getenv('HOME_ROUTE') + ad_images.file
            if os.getenv('ENV') == 'PRODUCTION':
                images = app.config['S3_LOCATION'] + ad_images.file
            ad_filter = {"id": advertisement.id, "title": advertisement.title,
                         "cover_image": images, "featured": advertisement.is_featured,
                         "location": advertisement.location, "price": advertisement.price,
                         "status": advertisement.status, "favourite": is_liked, "disabled": advertisement.is_disabled}
            my_advertisement_list.append(ad_filter)
    return {"data": {"message": my_advertisement_list}}, 200

@ad.route("/my_favourite_ad", methods=["GET"])
@jwt_required()
def my_favourite_ads():
    person=get_jwt_identity()
    favourites=FavouriteAd.query.filter_by(user_id=person).order_by(FavouriteAd.created_at.desc()).all()
    my_favourite_list=[]
    if favourites:
        for favourite in favourites:
            advertisement=Advertisement.query.filter(Advertisement.id==favourite.ad_id).first()
            if not advertisement.is_disabled:
                ad_images = AdImage.query.filter_by(ad_id=advertisement.id, is_cover_image=True).first()
                if os.getenv('ENV') == 'DEVELOPMENT':
                    images = os.getenv('HOME_ROUTE') + ad_images.file
                if os.getenv('ENV') == 'PRODUCTION':
                    images = app.config['S3_LOCATION'] + ad_images.file
                ad_filter = {"id": advertisement.id, "title": advertisement.title,
                             "cover_image": images, "featured": advertisement.is_featured,
                             "location": advertisement.location, "price": advertisement.price,
                             "status": advertisement.status, "favourite": True}
                my_favourite_list.append(ad_filter)
    return {"data": {"message": my_favourite_list}}, 200

@ad.route("/report_ad/<int:ad_id>", methods=["POST"])
@jwt_required()
def report_ads(ad_id):
    person = get_jwt_identity()
    if filtering_ad_by_id(ad_id) is None:
        return {"data": {"error": "ad not found"}}, 400
    if ReportAd.query.filter(ReportAd.ad_id == ad_id, ReportAd.user_id == person).first():
        return {"data": {"error": "ad already reported by the same user"}}, 409
    report_the_ad = ReportAd(user_id=person, ad_id=ad_id)
    db.session.add(report_the_ad)
    db.session.commit()
    if ReportAd.query.filter(ReportAd.ad_id == ad_id).count() >= app.config['COUNT_OF_REPORTS']:
        advertisement = Advertisement.query.filter_by(id=ad_id).first()
        advertisement.is_disabled = True
        db.session.add(advertisement)
        db.session.commit()
    return {"data": {"message": "ad reported"}}, 200


















































































































