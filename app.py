from createapp import get_app
from database import get_db
from advertisement.api import socketio
from user import register_user_blueprint
from flask_cors import CORS
from advertisement import register_ad_blueprint
from dotenv import load_dotenv
import os
from flasgger import Swagger, swag_from

load_dotenv()
app = get_app()
db = get_db()
swagger = Swagger(app)
register_user_blueprint()
register_ad_blueprint()

from user.models import User, UserProfile
from advertisement.models import Advertisement, AdImage, AdPlan, ReportAd, FavouriteAd
with app.app_context():
    db.create_all()
    db.session.commit()
CORS(app)

if __name__ == '__main__':
    socketio.run(app, host=os.getenv("HOST"), port=int(os.getenv("PORT")), allow_unsafe_werkzeug=True)

