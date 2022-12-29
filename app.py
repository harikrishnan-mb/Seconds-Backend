from createapp import get_app
from database import get_db
from user import register_user_blueprint
from flask_cors import CORS
from advertisement import register_ad_blueprint

app = get_app()
db = get_db()

register_user_blueprint()
register_ad_blueprint()

from user.models import User, UserProfile
from advertisement.models import Advertisement, AdImage, AdPlan, ReportAd, FavouriteAd
with app.app_context():
    db.create_all()
    db.session.commit()
CORS(app)

if __name__ == '__main__':
    app.run(host='10.6.9.26',port=5000)
