from flask import Blueprint,url_for,request
import re
from advertisement.models import db, Category, Advertisement, AdImage, AdPlan
from user.api import check_email
from user.models import User
ad=Blueprint('ad',__name__)
import os
import secrets
import string
from werkzeug.utils import secure_filename
from user.api import get_jwt_identity,jwt_required
from createapp import get_app
app = get_app()
@ad.route("/list_every_category", methods=["GET"])
def list_every_category():
    categories=Category.query.filter_by(parent_id=None).all()
    categories_list=[]
    for category in categories:
        sub_categories_list=[]
        sub_categories = Category.query.filter_by(parent_id=category.id).all()
        for sub_category in sub_categories:
            sub_category_name = {"id": sub_category.id, "name": sub_category.name}
            sub_categories_list.append(sub_category_name)
        category_name={"id":category.id, "name": category.name, "images": "http://10.6.9.26:5000"+'/'+category.image, "sub_category": sub_categories_list}
        categories_list.append(category_name)
    return{"data": {"message": categories_list}}, 200


@ad.route("/category", methods=["GET"])
def list_category():
    categories=Category.query.filter_by(parent_id=None).all()
    categories_list=[]
    for category in categories:
        category_name={"id":category.id, "name": category.name, "images": "http://10.6.9.26:5000"+'/'+category.image}
        categories_list.append(category_name)
    return{"data": {"message": categories_list}}, 200


@ad.route("/sub_category/<int:parent_id>", methods=["GET"])
def list_all_sub_category(parent_id):
    sub_categories=Category.query.filter_by(parent_id=parent_id).all()
    sub_categories_list=[]
    for sub_category in sub_categories:
        sub_category_name = {"id": sub_category.id, "name": sub_category.name}
        sub_categories_list.append(sub_category_name)
    return{"data": {"message": sub_categories_list}}, 200


@ad.route("/category_delete/<int:category_id>", methods=["DELETE"])
@jwt_required()
def delete_category(category_id):
    person = get_jwt_identity()
    filter_user = User.query.filter_by(id=person).first()
    if filter_user.is_admin is True:
        filter_category = Category.query.filter_by(id=category_id).first()
        if filter_category:
            try:
                os.remove(os.path.join(app.config['UPLOADED_ITEMS_DEST'], filter_category.image))
            except:
                pass
            db.session.delete(filter_category)
            db.session.commit()
            return {"data": {"message": "category removed"}}
        else:
            return {"data": {"error": "category does not exist"}}
    else:
        return {"data": {"error": "only admin can access this route"}}

ALLOWED_EXTENSIONS = {'svg'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ad.route("/add_category", methods=["POST"])
@jwt_required()
def add_category():
    person = get_jwt_identity()
    filter_user = User.query.filter_by(id=person).first()
    if filter_user.is_admin is True:
        name = request.form.get("name")
        file = request.files.get('file')
        parent_id = request.form.get("parent_id")
        if not name:
            return {"data": {"error": "provide category name"}}
        if name and not file and not parent_id or name and file and parent_id:
            return {"data" : {"error": "provide parent_id or file"}}
        filter_category = Category.query.filter_by(name=name).first()
        if filter_category:
            return {"data": {"error": "category already exist"}}
        if parent_id and file:
            return{"data": {"error": "provide image if category and provide parent_id if sub category"}}
        check_ids = Category.query.filter_by(id=parent_id).first()
        if parent_id:
            if not check_ids:
                return  {"data": {"error": "parent_id should be id of any category"}}
            else:
                category_add = Category(name, "", parent_id)
        if not parent_id or parent_id=='':
            if not file:
                return {"data":{"error": "image is required for the category"}}
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                category_add=Category(name, 'static/catagory/'+ filename, parent_id)
        db.session.add(category_add)
        db.session.commit()
        return {"data": {"message": "Category created"}}
    else:
        return {"data": {"error": "only admin can add category"}}


@ad.route("/update_category/<int:category_id>", methods=["PUT"])
@jwt_required()
def change_category(category_id):
    person = get_jwt_identity()
    filter_user = User.query.filter_by(id=person).first()
    if filter_user.is_admin is True:
        name = request.form["name"]
        file = request.files.get('file')
        parent_id = request.form.get("parent_id")
        if not name:
            return {"data": {"error": "provide category name"}}
        filter_category = Category.query.filter_by(name=name).first()
        category_update = Category.query.filter_by(id=category_id).first()
        if filter_category:
            return {"data": {"error": "category already exist"}}
        if parent_id:
            check_ids = Category.query.filter_by(id=parent_id).first()
            if not check_ids:
                {"data": {"error": "parent_id should be id of any category"}}
            try:
                os.remove(os.path.join(app.config['UPLOADED_ITEMS_DEST'], filter_category.image))
            except:
                pass
            category_update.name=name
            category_update.image=''
            category_update.parent_id=parent_id
        if not parent_id or parent_id=='':
            if not file:
                return {"data":{"error": "image is required for the category"}}
            if file and allowed_file(file.filename):
                try:
                    os.remove(os.path.join(app.config['UPLOADED_ITEMS_DEST'], filter_category.image))
                except:
                    pass
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                category_update.name = name
                category_update.image = 'static/catagory/'+ filename
                category_update.parent_id = parent_id
        db.session.add(category_update)
        db.session.commit()
        return {"data": {"message": "Category updated"}}
    else:
        return {"data": {"error": "only admin can add category"}}

@ad.route("/ad_plan", methods=["GET"])
def list_ad_plan():
    ad_plans=AdPlan.query.all()
    ad_plan_list=[]
    for ad_plan in ad_plans:
        ad_plan_name={"id": ad_plan.id, "price": ad_plan.price, "days": ad_plan.days}
        ad_plan_list.append(ad_plan_name)
    return{"data": {"message": ad_plan_list}}, 200
def allowed_img_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png','jpg','jpeg'}
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
        return {"data":{"error": "provide category id"}}
    for image in images:
        if image.filename == '':
            return {"data":{"error": "provide image"}}
        if image and not allowed_img_file(image.filename):
            return {"data":{"error": "image should be in png, jpg or jpeg format"}}
    try:
        category_id=int(category_id)
    except ValueError:
        return {"data": {"error": "provide category id as integer"}}
    if Category.query.filter_by(id=int(category_id)).first() is None:
        return {"data": {"error": "category id not found"}}
    if not title:
        return {"data": {"error": "provide title"}}
    if not status:
        status='active'
    if not seller_type:
        return {"data": {"error": "provide seller_type"}}
    if not description:
        description=''
    if not price:
        return {"data": {"error": "provide price"}}
    try:
        price = float(price)
    except ValueError:
        return {"data": {"error": "provide price as floating number"}}
    if not negotiable_product:
        return {"data": {"error": "provide product is negotiable or not"}}
    if negotiable_product.capitalize()=="True":
        negotiable_product=True
    elif negotiable_product.capitalize()=="False":
        negotiable_product=False
    else:
        return {"data": {"error": "provide product is negotiable or not as True or False"}}
    if not feature_product:
        return {"data": {"error": "provide product is featured or not"}}
    if feature_product.capitalize()=="True":
        feature_product=True
    elif feature_product.capitalize()=="False":
        negotiable_product=False
    else:
        return {"data": {"error": "provide product is featured or not as True or False"}}
    if not ad_plan_id:
        return {"data": {"error": "provide advertisement plan id"}}
    try:
        ad_plan_id=int(ad_plan_id)
    except ValueError:
        return {"data": {"error": "provide advertisement plan id as integer"}}
    if not AdPlan.query.filter_by(id=ad_plan_id).first():
        return {"data": {"error": "advertisement plan id not found"}}
    if not location:
        return {"data": {"error": "provide location"}}
    if not latitude:
        return {"data": {"error": "provide latitude"}}
    try:
        latitude_location = float(latitude)
    except ValueError:
        return {"data": {"error": "provide latitude as floating number"}}
    if not longitude:
        return {"data": {"error": "provide longitude"}}
    try:
        longitude_location = float(longitude)
    except ValueError:
        return {"data": {"error": "provide longitude as floating number"}}
    if  float(longitude) is False:
        return {"data": {"error": "provide longitude as floating number"}}
    if not phone:
        return {"data":{"error": "provide phone number"}}
    if not check_phone(phone):
        return {"data": {"error": "provide valid phone number"}}
    if not email_id:
        return {"data": {"error": "provide email"}}
    if not check_email(email_id):
        return {"data": {"error": "provide valid email"}}

    ad_1 = Advertisement(title=title, user_id=get_jwt_identity(), description=description, category_id=category_id, status=status, seller_type=seller_type, price=price, advertising_plan_id=ad_plan_id,
                         is_negotiable=negotiable_product, is_featured= feature_product, location=location, latitude=latitude, longitude=longitude,
                         seller_name=seller_name, phone=phone, email=email_id, advertising_id=generate_random_text())
    db.session.add(ad_1)
    db.session.commit()
    for image in images:
        display_order=images.index(image)+1
        if images.index(image)==0:
            cover_image=True
        else:
            cover_image=False
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_AD_PICTURE'], filename))
        ad_image_1 = AdImage(display_order=display_order, file='static/images_ad/'+filename, is_cover_image=cover_image, ad_id=ad_1.id)
        db.session.add(ad_image_1)
    db.session.commit()
    return {"data": {"message": "ad created"}}
def generate_random_text():
    return ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(20))


def check_phone(phone):
    phone_num = "[6-9][0-9]{9}"
    if re.fullmatch(phone_num, phone):
        return True
    else:
        return False























































