import createapp

from user.api import user


def register_user_blueprint():
    app = createapp.get_app()
    app.register_blueprint(user, url_prefix='/user')
