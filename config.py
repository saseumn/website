import os
import sys

from oauth2client import client, tools
from oauth2client.file import Storage


SCOPES = "https://www.googleapis.com/auth/gmail.send"


class Config(object):
    """ Configuration for the Flask object based on environment variables. """

    def __init__(self):
        # ENVIRONMENT = { development | testing | production }
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "production")  # secure by defualt
        if self.ENVIRONMENT.lower() == "development":
            self.DEBUG = True
            self.TEMPLATES_AUTO_RELOAD = True

        self.port = int(os.getenv("PORT", "7400"))

        # Secret Key
        self.SECRET_KEY = Config.get_secret_key()

        # Database URL
        self.SQLALCHEMY_DATABASE_URI = Config.get_database_url()
        self.SQLALCHEMY_TRACK_MODIFICATIONS = True

        # Flask-Admin
        self.SECURITY_URL_PREFIX = os.getenv("SECURITY_URL_PREFIX", "/admin")

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
        credentials_path = os.getenv("GMAIL_CREDENTIAL_FILE")
        if not credentials_path:
            return False
        store = Storage(credentials_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            client_secret_path = os.getenv("GMAIL_CLIENT_SECRET")
            if not client_secret_path:
                return False
            flow = client.flow_from_clientsecrets(client_secret_path, SCOPES)
            flow.user_agent = "SASE UMN Website"
            credentials = tools.run_flow(flow, store)
        return credentials
