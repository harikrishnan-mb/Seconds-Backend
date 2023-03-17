from advertisement.models import db, Category, AdPlan, Advertisement, AdImage, FavouriteAd
from sqlalchemy.orm import Session
from user.models import User
import os
from flask import request
from s3config import s3
import secrets
import string
from werkzeug.utils import secure_filename
from createapp import get_app
from sqlalchemy import create_engine
from user.api import get_jwt_identity, verify_jwt_in_request
from datetime import datetime, timedelta
from sqlalchemy import func, or_, and_
app = get_app()
engine = create_engine(os.getenv("ENGINE"))


def get_every_categories(categories_list):
    for category in filtering_main_category():
        sub_categories_list = []
        for sub_category in Category.query.filter_by(parent_id=category.id).all():
            sub_category_name = {"id": sub_category.id, "name": sub_category.name}
            sub_categories_list.append(sub_category_name)
        if os.getenv('ENV') == 'DEVELOPMENT':
            category_name = {"id": category.id, "name": category.name, "images": os.getenv("HOME_ROUTE")+category.image, "sub_category": sub_categories_list}
        if os.getenv('ENV') == 'PRODUCTION':
            category_name = {"id": category.id, "name": category.name,"images": app.config['S3_LOCATION'] + category.image, "sub_category": sub_categories_list}
        categories_list.append(category_name)
    return {"data": {"message": categories_list}}, 200


def filtering_main_category():
    return Category.query.filter_by(parent_id=None).order_by(Category.id).all()


def get_only_categories(categories_list):
    for category in filtering_main_category():
        if os.getenv('ENV') == 'DEVELOPMENT':
            category_name = {"id": category.id, "name": category.name, "images": os.getenv("HOME_ROUTE")+category.image}
        if os.getenv('ENV') == 'PRODUCTION':
            category_name = {"id": category.id, "name": category.name, "images": app.config['S3_LOCATION'] + category.image}
        categories_list.append(category_name)
    return{"data": {"message": categories_list}}, 200


def admin_is_true(person):
    return User.query.filter_by(id=person).first().is_admin


def deleting_the_category(category_id):
    db.session.delete(filtering_category(category_id))
    db.session.commit()
    return {"data": {"message": "category removed"}}, 200


def deleting_the_category(category_id):
    db.session.delete(filtering_category(category_id))
    db.session.commit()
    return {"data": {"message": "category removed"}}, 200


def checking_category_name_already_exist(category):
    return Category.query.filter_by(name=category).first()


def checking_parent_id_exist(parent_id):
    return Category.query.filter_by(id=parent_id).first()


def adding_category_to_db(category_add):
    db.session.add(category_add)
    db.session.commit()
    return {"data": {"message": "Category created"}}, 200


def checking_new_and_old_category_name_not_same(category_id, category):
    return filtering_category(category_id).name != category


def filtering_category(category_id):
    return Category.query.filter_by(id=category_id).first()


def updating_category_in_db(category_id):
    db.session.add(filtering_category(category_id))
    db.session.commit()
    return {"data": {"message": "Category updated"}}, 200


def ads_plan(ad_plan_list):
    ad_plans = AdPlan.query.order_by(AdPlan.id.asc()).all()
    for ad_plan in ad_plans:
        ad_plan_name = {"id": ad_plan.id, "price": ad_plan.price, "days": ad_plan.days}
        ad_plan_list.append(ad_plan_name)
    return {"data": {"message": ad_plan_list}}, 200


def checking_user_posted_ad(del_ad_id, person):
    return filtering_ad_by_id(del_ad_id).user_id == person


def deleting_ad(del_ad_id):
    filtering_ad_by_id(del_ad_id).is_deleted = True
    db.session.add(filtering_ad_by_id(del_ad_id))
    db.session.commit()
    return {"data": {"message": "ad deleted"}}, 200


def filtering_ad_by_id(del_ad_id):
    return Advertisement.query.filter_by(id=del_ad_id).first()


def generate_random_text():
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(14))


def saving_created_ad(title, description, category_id, status, seller_type, price, ad_plan_id, negotiable_product,
                      feature_product, location, latitude, longitude, seller_name, phone, email_id, images, geo):
    with Session(engine) as session:
        session.begin()
        try:
            ad_1 = Advertisement(title=title, user_id=get_jwt_identity(), description=description,
                                 category_id=category_id, status=status, seller_type=seller_type, price=price,
                                 advertising_plan_id=ad_plan_id, is_deleted=False, is_negotiable=negotiable_product,
                                 is_featured=feature_product,location=location, latitude=latitude, longitude=longitude,
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
                if os.getenv('ENV') == 'DEVELOPMENT':
                    image.save(os.path.join(app.config['UPLOAD_AD_PICTURE'], filename))
                if os.getenv('ENV') == 'PRODUCTION':
                    s3.upload_fileobj(image, app.config['S3_BUCKET'], 'static/images_ad/' + filename,
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
        if "Authorization" in request.headers:
            verify_jwt_in_request()
            person = get_jwt_identity()
            if FavouriteAd.query.filter_by(ad_id=advertisement.id, user_id=person).first():
                is_liked = True
        ad_images = AdImage.query.filter_by(ad_id=advertisement.id, is_cover_image=True).first()
        if os.getenv('ENV') == 'DEVELOPMENT':
            images = os.getenv('HOME_ROUTE') + ad_images.file
        if os.getenv('ENV') == 'PRODUCTION':
            images = app.config['S3_LOCATION'] + ad_images.file
        ad_filter = {"id": advertisement.id, "title": advertisement.title, "cover_image": images,
                     "featured": advertisement.is_featured, "location": advertisement.location,
                     "price": advertisement.price, "status": advertisement.status, "favourite": is_liked}
        list_ad.append(ad_filter)
    return {"data": {"message": list_ad, "count": number_of_ads, "below_one_lakh": count_of_price_range_0_to_1_lakh,
                     "one_to_three_lakh": count_of_price_range_1_to_3_lakh,
                     "three_to_six_lakh": count_of_price_range_3_to_6_lakh,
                     "above_six_lakh": count_of_price_range_greater_than_6_lakh}}, 200


def updating_ad_details(title, person, description, category_id, status, seller_type, price, ad_plan_id,
                        negotiable_product, feature_product, location, latitude, longitude, seller_name,
                        phone, email_id, images, ads_id, geo):
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
        adv.updated_at = datetime.now()
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
                s3.upload_fileobj(image, app.config['S3_BUCKET'], 'static/images_ad/' + filename,
                                  ExtraArgs={"ACL": "public-read", "ContentType": image.content_type})
            ad_image_1 = AdImage(display_order=display_order,
                                 file='static/images_ad/' + filename, is_cover_image=cover_image, ad_id=adv.id)
            db.session.add(ad_image_1)
        db.session.commit()
        return {"data": {"message": "ad edited successfully"}}, 200
    except:
        return {"data": {"error": "error uploading image"}}, 400
