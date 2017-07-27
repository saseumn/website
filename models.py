from flask_sqlalchemy import SQLAlchemy
from passlib.hash import bcrypt
from sqlalchemy.ext.hybrid import hybrid_property

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True, index=True)
    email_verified = db.Column(db.Boolean)
    email_verification_token = db.Column(db.String(256), index=True)
    _password = db.Column("password", db.String(256))

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = bcrypt.encrypt(password, rounds=10)

    def check_password(self, password):
        return bcrypt.verify(password, self.password)
