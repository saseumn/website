from flask_admin import Admin
from flask_login import LoginManager
from flask_security import Security, SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy

login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message_category = "danger"

db = SQLAlchemy()

user_datastore = None
security = None

admin_role = None
board_role = None

admin = Admin(base_template="admin/base.html")


def init_security(app, User, Role):
    global user_datastore, security, admin_role, board_role

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    # with app.app_context():
    #     admin_role = Role.query.filter_by(name="admin").first()
    #     flag = False
    #     if not admin_role:
    #         admin_role = Role(name="admin", description="Site Administrator")
    #         db.session.add(admin_role)
    #         flag = True
    #     board_role = Role.query.filter_by(name="board").first()
    #     if not board_role:
    #         board_role = Role(name="board", description="SASE UMN Board Member")
    #         db.session.add(board_role)
    #         flag = True
    #     if flag:
    #         db.session.commit()

    return security
