from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from passlib.hash import bcrypt
from sqlalchemy.ext.hybrid import hybrid_property

from ext import login_manager

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(32))
    username = db.Column(db.String(16), unique=True, index=True)
    admin = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(256), unique=True, index=True)
    email_verified = db.Column(db.Boolean)
    email_verification_token = db.Column(db.String(256), index=True)
    _register_time = db.Column("register_time", db.DateTime, default=datetime.now)
    _password = db.Column("password", db.String(256))

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = bcrypt.encrypt(password, rounds=10)

    def check_password(self, password):
        return bcrypt.verify(password, self.password)

    @staticmethod
    @login_manager.user_loader
    def get_by_id(id):
        query_results = User.query.filter_by(id=id)
        return query_results.first()

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    def get_id(self):
        return str(self.id)
