import logging
import time
import sys

from flask import Flask, url_for
from flask_admin import helpers as admin_helpers

from saseumn.admin import SecuredHomeView, RoleView, EventView, UserView
from saseumn.config import Config
from saseumn.models import Role, User
from saseumn.objects import admin, db, init_security, login_manager


def make_app(config=None, testing=None):
    """ Returns a Flask object ready to serve the website. """

    if not config:
        if not testing:
            testing = False
        config = Config(testing=testing)

    # Create a Flask app object.
    app = Flask(__name__)
    app.config.from_object(config)

    @app.after_request
    def after_request(response):
        if app.config.get("ENVIRONMENT") == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    @app.template_filter("to_timestamp")
    def to_timestamp(d):
        return int(time.mktime(d.timetuple()))

    # Initialize
    admin.init_app(app, index_view=SecuredHomeView(url="/admin"))
    db.init_app(app)
    login_manager.init_app(app)
    security = init_security(app, User, Role)

    app.db = db

    @security.context_processor
    def security_context_processor():
        return dict(
            admin_base_template=admin.base_template,
            admin_view=admin.index_view,
            h=admin_helpers,
            get_url=url_for
        )

    # Admin stuff
    admin.add_view(RoleView(db.session))
    admin.add_view(EventView(db.session))
    admin.add_view(UserView(db.session))

    # Register endpoints.
    import saseumn.views as views
    app.register_blueprint(views.base.blueprint)
    app.register_blueprint(views.users.blueprint, url_prefix="/users")

    return app


if __name__ == "__main__":
    config = Config()
    app = make_app(config)
    app.run(port=config.port)
