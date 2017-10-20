from datetime import datetime

from flask import url_for
from passlib.hash import bcrypt
from sqlalchemy.ext.hybrid import hybrid_property
from flask_security import UserMixin, RoleMixin

from saseumn.objects import login_manager
from saseumn.objects import db
from saseumn.util import random_string

attendance = db.Table("attendance", db.Model.metadata,
                      db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
                      db.Column("event_id", db.Integer, db.ForeignKey("events.id")))

roles_users = db.Table("roles_users",
                       db.Column("user_id", db.Integer(), db.ForeignKey("users.id")),
                       db.Column("role_id", db.Integer(), db.ForeignKey("roles.id")))


class Role(db.Model, RoleMixin):
    __tablename__ = "roles"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    active = db.Column(db.Boolean)
    token = db.Column(db.String(length=16), default=lambda: random_string(length=16))
    email = db.Column(db.Unicode(length=128))
    expire = db.Column(db.DateTime)

    @property
    def expired(self):
        return datetime.utcnow() >= self.expire

    @property
    def user(self):
        return User.get_by_id(self.uid)


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))
    location = db.Column(db.Text)
    description = db.Column(db.Text)
    published = db.Column(db.Boolean, default=False)
    start_time = db.Column(db.DateTime)
    registration_key = db.Column(db.String(32), default=lambda: random_string(length=24))

    attendees = db.relationship("User", secondary=attendance, backref="events")

    @property
    def registration_link(self):
        return url_for("users.register", evtkey=self.registration_key, _external=True)


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(32))
    username = db.Column(db.String(16), unique=True, index=True)
    _admin = db.Column("admin", db.Boolean, default=False)
    email = db.Column(db.String(256), unique=True, index=True)
    email_verified = db.Column(db.Boolean)
    email_verification_token = db.Column(db.String(256), index=True)
    _register_time = db.Column("register_time", db.DateTime, default=datetime.now)
    _password = db.Column("password", db.String(256))
    roles = db.relationship("Role", secondary=roles_users, backref=db.backref("users", lazy="dynamic"))

    @hybrid_property
    def admin(self):
        return self._admin

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

    # these are here to satisfy flask-security, we don't really need them yet
    @property
    def active(self):
        return True

    @active.setter
    def active(self, value):
        return
