import os


class Config(object):
    """ Configuration for the Flask object based on environment variables. """

    def __init__(self):
        # ENVIRONMENT = { development | testing | production }
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        if self.ENVIRONMENT.lower() == "development":
            self.DEBUG = True

        self.port = int(os.getenv("PORT", "7400"))
