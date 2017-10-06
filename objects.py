from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_admin import Admin

login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message_category = "danger"

db = SQLAlchemy()

user_datastore = None
security = None

admin = Admin()


def init_security(app, User, Role):
    global user_datastore, security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)
