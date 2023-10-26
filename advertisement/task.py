from celery import Celery
from createapp import get_app
from flask_mail import Message
from user.api import mail
from .models import Advertisement, AdPlan
from database import db
from datetime import datetime, timedelta
app = get_app()


celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])
celery.conf.update(app.config)


@celery.task
def send_ad_creation_email(email_of_user, title):
    with app.app_context():
        msg = Message('Advertisement created', sender='seconds.clone@gmail.com', recipients=[email_of_user])
        msg.body = f'Advertisement titled "{title}" created successfully'
        msg.html = f'<p style="color: blue;">Advertisement titled "{title}" created successfully</p>'
        mail.send(msg)


@celery.task
def checking_if_featured_ad_expired():
    adv = Advertisement.query.filter_by(is_featured=True).all()
    for ads in adv:
        plan = AdPlan.query.filter_by(id=ads.advertising_plan_id).first()
        if datetime.now()-ads.created_at > timedelta(days=plan.days):
            ads.is_featured = False
            db.session.add(ads)
            db.session.commit()


