from flask import Flask

from config import Config


def make_app(config=None):
    """ Returns a Flask object ready to serve the website. """

    if not config:
        config = Config()

    # Create a Flask app object.
    app = Flask(__name__)
    app.config.from_object(config)

    # Register endpoints.
    import views
    app.register_blueprint(views.base.blueprint)

    return app


config = Config()
app = make_app(config)

if __name__ == "__main__":
    app.run(port=config.port)
