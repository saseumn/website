import logging
import sys

from flask import Flask

from config import Config
from models import Role, User
from objects import admin, db, init_security, login_manager


def make_app(config=None):
    """ Returns a Flask object ready to serve the website. """

    if not config:
        config = Config()

    # Create a Flask app object.
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize
    admin.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    init_security(app, User, Role)

    # Admin stuff
    import admin as admin_views
    # admin.add_view(admin_views.GenericModelView(Role, db.session, endpoint="lol"))

    # Register endpoints.
    import views
    # app.register_blueprint(views.base.blueprint)
    # app.register_blueprint(views.users.blueprint, url_prefix="/users")

    return app


config = Config()
app = make_app(config)

if __name__ == "__main__":
    app.run(port=config.port)
