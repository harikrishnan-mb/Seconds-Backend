from flask import Blueprint,url_for,request
from advertisement.models import db, Category
from user.models import User
ad=Blueprint('ad',__name__)
import os
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
        category_name={"id":category.id, "name": category.name, "images": "http://127.0.0.1:5000"+category.image, "sub_category": sub_categories_list}
        categories_list.append(category_name)
    return{"data": {"message": categories_list}}, 200


@ad.route("/category", methods=["GET"])
def list_category():
    categories=Category.query.filter_by(parent_id=None).all()
    categories_list=[]
    for category in categories:
        category_name={"id":category.id, "name": category.name, "images": "http://127.0.0.1:5000"+category.image}
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
                category_add=Category(name, '/static/catagory/'+ filename, parent_id)
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
            category_update.name=name
            category_update.image=''
            category_update.parent_id=parent_id
        if not parent_id or parent_id=='':
            if not file:
                return {"data":{"error": "image is required for the category"}}
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                category_update.name = name
                category_update.image = '/static/catagory/'+ filename
                category_update.parent_id = parent_id
        db.session.add(category_update)
        db.session.commit()
        return {"data": {"message": "Category updated"}}
    else:
        return {"data": {"error": "only admin can add category"}}























