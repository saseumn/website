import os
import sys


class Config(object):
    """ Configuration for the Flask object based on environment variables. """

    def __init__(self):
        # ENVIRONMENT = { development | testing | production }
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        if self.ENVIRONMENT.lower() == "development":
            self.DEBUG = True

        self.port = int(os.getenv("PORT", "7400"))

        # Secret Key
        self.SECRET_KEY = Config.get_secret_key()

        # Database URL
        self.SQLALCHEMY_DATABASE_URI = Config.get_database_url()

    @staticmethod
    def get_database_url():
        url = os.getenv("DATABASE_URL")
        if not url:
            sys.stderr.write("DATABASE_URL not specified, application is exiting..\n")
            sys.stderr.flush()
            sys.exit(1)
        return url

    @staticmethod
    def get_secret_key():
        key = os.getenv("SECRET_KEY")
        if key:
            return key
        sys.stderr.write("DATABASE_URL not specified, application is exiting..\n")
        sys.stderr.flush()
        sys.exit(1)
