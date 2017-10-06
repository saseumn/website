import logging
import sys

from flask import Flask, url_for
from flask_admin import helpers as admin_helpers

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
    security = init_security(app, User, Role)

    @security.context_processor
    def security_context_processor():
        return dict(
            admin_base_template=admin.base_template,
            admin_view=admin.index_view,
            h=admin_helpers,
            get_url=url_for
        )

    # Admin stuff
    import admin as admin_views
    admin.add_view(admin_views.RoleView(db.session))
    admin.add_view(admin_views.UserView(db.session))

    # Register endpoints.
    import views
    app.register_blueprint(views.base.blueprint)
    app.register_blueprint(views.users.blueprint, url_prefix="/users")

    return app


if __name__ == "__main__":
    config = Config()
    app = make_app(config)
    app.run(port=config.port)
