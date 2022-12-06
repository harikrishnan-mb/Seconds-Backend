from createapp import get_app
from database import get_db

app = get_app()
db = get_db()

from user.models import User, UserProfile
from  advertisement.models import Advertisement, AdImage, AdPlan, ReportAd, FavouriteAd
with app.app_context():
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    app.run(port=5001)
