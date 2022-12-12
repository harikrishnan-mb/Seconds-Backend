import createapp
from advertisement.api import ad

def register_ad_blueprint():
    app = createapp.get_app()
    app.register_blueprint(ad, url_prefix='/ad')