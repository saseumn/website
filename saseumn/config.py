import os
import sys
import logging


class Config(object):
    """ Configuration for the Flask object based on environment variables. """

    def __init__(self, testing=False):
        self.port = int(os.getenv("PORT", "7400"))

        self.SECRET_KEY = Config.get_secret_key()
        self.SQLALCHEMY_TRACK_MODIFICATIONS = True

        # Flask-Admin
        self.SECURITY_URL_PREFIX = os.getenv("SECURITY_URL_PREFIX", "/admin")

        # ENVIRONMENT = { development | testing | production }
        self.ENVIRONMENT = os.getenv(
            "ENVIRONMENT", "production")  # secure by defualt

        self.UPLOADS_DIRECTORY = self.get_uploads_directory()

        if self.ENVIRONMENT.lower() == "development":
            self.DEBUG = True
            self.EMAIL_VERIFICATION_DISABLED = True
            self.TEMPLATES_AUTO_RELOAD = True

        if testing or self.ENVIRONMENT.lower() == "testing":
            self.DEBUG = True
            self.EMAIL_VERIFICATION_DISABLED = True
            self.SERVER_NAME = "localhost"
            self.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
            self.TESTING = True
            self.WTF_CSRF_ENABLED = False
        else:
            self.SQLALCHEMY_DATABASE_URI = Config.get_database_url()

    @staticmethod
    def get_database_url():
        url = os.getenv("DATABASE_URL")

        if not url:
            sys.stderr.write(
                "DATABASE_URL not specified, application is exiting..\n")
            sys.stderr.flush()
            sys.exit(1)
        return url

    @staticmethod
    def get_secret_key():
        key = os.getenv("SECRET_KEY")
        if key:
            return key
        sys.stderr.write(
            "SECRET_KEY not specified, application is exiting..\n")
        sys.stderr.flush()
        sys.exit(1)

    @staticmethod
    def get_email_credentials():
        gmail_username = os.getenv("GMAIL_USERNAME")
        gmail_password = os.getenv("GMAIL_PASSWORD")
        if not (gmail_username and gmail_password):
            return False
        return (gmail_username, gmail_password)

    @staticmethod
    def get_uploads_directory():
        parent = os.path.dirname(os.path.realpath(__file__))
        path = os.getenv("UPLOADS_DIRECTORY", os.path.join(parent, "uploads"))
        if not os.path.exists(path):
            os.makedirs(path)
        return path
