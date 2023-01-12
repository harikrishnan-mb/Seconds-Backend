
from datetime import datetime
from database import get_db
from geoalchemy2 import Geography
db = get_db()


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=True)
    image = db.Column(db.Text, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    # Relationship
    advertisements = db.relationship('Advertisement', backref='category')

    def __init__(self, name, image, parent_id):
        self.name = name
        self.image = image
        self.parent_id = parent_id

    def __str__(self):
        return f"Category  with name {self.name} and id {self.id} and {self.parent_id} created"


class AdPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float)
    days = db.Column(db.Integer)

    # Relationship
    advertisements = db.relationship('Advertisement', backref='ad_plan')

    def __init__(self, price, days):
        self.days = days
        self.price = price

    def __str__(self):
        return f"Plan for {self.days} days and price{self.price}"


class Advertisement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(400), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    status = db.Column(db.String(40))
    seller_type = db.Column(db.String(40))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    advertising_plan_id = db.Column(db.Integer, db.ForeignKey('ad_plan.id'))
    is_negotiable = db.Column(db.Boolean, default=False, nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    location = db.Column(db.Text)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    geo = db.Column(Geography(geometry_type="POINT", srid=4326))
    seller_name = db.Column(db.String(100))
    phone = db.Column(db.BigInteger, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    advertising_id = db.Column(db.String(100), unique=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=datetime.utcnow())

    # Relationship
    report_ads = db.relationship('ReportAd', backref='advertisement')
    favourite_ads = db.relationship('FavouriteAd', backref='advertisement')
    ad_images = db.relationship('AdImage', backref='advertisement')
    # messages = db.relationship('Message', backref='advertisement')

    def __init__(self, title, status, seller_type, description, price, is_negotiable, is_featured, location, latitude,
                 longitude, geo, seller_name, phone, email,is_deleted, advertising_id, user_id, category_id, advertising_plan_id):
        self.title = title
        self.status = status
        self.seller_type = seller_type
        self.description = description
        self.price = price
        self.is_negotiable = is_negotiable
        self.is_featured = is_featured
        self.location = location
        self.latitude = latitude
        self.longitude = longitude
        self.seller_name = seller_name
        self.geo=geo
        self.email = email
        self.phone = phone
        self.advertising_id = advertising_id
        self.user_id = user_id
        self.category_id = category_id
        self.advertising_plan_id = advertising_plan_id
        self.is_deleted = is_deleted

    def __str__(self):
        return f"Ad with {self.title} created"



class AdImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    display_order = db.Column(db.Integer, nullable=False)
    file = db.Column(db.Text, nullable=False)
    is_cover_image = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    ad_id = db.Column(db.Integer, db.ForeignKey('advertisement.id'))

    def __init__(self, display_order, file, is_cover_image, ad_id):
        self.display_order = display_order
        self.file = file
        self.is_cover_image = is_cover_image
        self.ad_id = ad_id

    def __str__(self):
        return f"Ad Image with {self.id} as id uploaded"


class ReportAd(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'))
    ad_id = db.Column(db.Integer, db.ForeignKey('advertisement.id'))

    def __init__(self, user_id, ad_id):
        self.user_id = user_id
        self.ad_id = ad_id

    def __str__(self):
        return f"Ad Image with {self.id} as id reported"


class FavouriteAd(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ad_id = db.Column(db.Integer, db.ForeignKey('advertisement.id'))

    def __init__(self, user_id, ad_id):
        self.user_id = user_id
        self.ad_id = ad_id

    def __str__(self):
        return f"Ad  with {self.id} as is add to favourites"

#
# class Message(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     ad_id = db.Column(db.Integer, db.ForeignKey('advertisement.id'))
#     content = db.Column(db.Text)
#     created_at = db.Column(db.DateTime, default=datetime.now())
#
#     def __init__(self, sender_id, receiver_id, ad_id, content):
#         self.sender_id = sender_id
#         self.receiver_id = receiver_id
#         self.content = content
#         self.ad_id = ad_id
#
#     def __str__(self):
#         return f"Message with {self.id} id is send"
