from flask import Flask, g, session
from flask.ext.bcrypt import Bcrypt

from .api import api
from .frontend import frontend
from .model import db, User
from .oauth import oauth


def configure_app(app):
    app.config.from_object('flask_simpleoauth.settings')

    db.init_app(app)
    app.bcrypt = Bcrypt(app)

    app.register_blueprint(frontend)

    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(oauth, url_prefix='/oauth')

    @app.before_request
    def before_request():
        g.user = None

        user_id = session.get('user_id')
        if user_id is not None:
            g.user = User.objects.with_id(user_id)


def create_app():
    app = Flask(__name__)
    configure_app(app)
    return app
