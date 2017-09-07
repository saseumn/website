from flask import Flask

from config import Config
from ext import login_manager
from models import db
import logging
import sys


def make_app(config=None):
    """ Returns a Flask object ready to serve the website. """

    if not config:
        config = Config()

    # Create a Flask app object.
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize
    db.init_app(app)
    login_manager.init_app(app)

    # Register endpoints.
    import views
    app.register_blueprint(views.admin.blueprint, url_prefix="/admin")
    app.register_blueprint(views.base.blueprint)
    app.register_blueprint(views.users.blueprint, url_prefix="/users")

    return app


config = Config()
app = make_app(config)

if __name__ == "__main__":
    app.run(port=config.port)
