"""
    users.py
    ~~~~~~~~

    Responsible for all user-related endpoints.
"""

import string
from datetime import datetime, timedelta

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_user, logout_user
from flask_wtf import FlaskForm
from sqlalchemy import func, or_
from wtforms import ValidationError
from wtforms.fields import (BooleanField, PasswordField, StringField,
                            SubmitField)
from wtforms.validators import Email, EqualTo, InputRequired, Length

from models import PasswordResetToken, User, db
from util import (VALID_USERNAME, get_redirect_target, random_string,
                  redirect_back, send_email)

blueprint = Blueprint("users", __name__, template_folder="templates")
email_template = """
Hello, $username!

You recently created an account with SASE UMN using this email. To prove you're
legit, please click on the following link (or copy-paste it into your browser
your email client didn't render a link).

$link

Thanks!
SASE UMN Webmasters
"""


@blueprint.route("/login", methods=["GET", "POST"])
def login():
    redirect_to = get_redirect_target()
    if current_user.is_authenticated:
        return redirect_back("base.index")
    login_form = LoginForm(remember=True)
    if login_form.validate_on_submit():
        user = login_form.get_user()
        if not user.admin and not user.email_verified:
            flash(
                "You haven't activated your account yet! Check your email for an activation email.", "danger")
            return redirect(url_for("users.login"))
        login_user(user)
        flash("Successfully logged in!", "success")
        return redirect_back("base.index")
    return render_template("users/login.j2", login_form=login_form, next=redirect_to)


@blueprint.route("/logout")
def logout():
    logout_user()
    flash("Successfully logged out!", "success")
    return redirect(url_for("base.index"))


@blueprint.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("base.index"))
    register_form = RegisterForm(prefix="register")
    if register_form.validate_on_submit():
        new_user = register_user(register_form.name.data,
                                 register_form.email.data,
                                 register_form.username.data,
                                 register_form.password.data,
                                 admin=False)
        flash("Check your email for an activation link.", "info")
        return redirect(url_for("users.login"))
    return render_template("users/register.j2", register_form=register_form)


@blueprint.route("/password/forgot", methods=["GET", "POST"])
def forgot():
    forgot_form = PasswordForgotForm()
    if forgot_form.validate_on_submit():
        if forgot_form.user is not None:
            token = PasswordResetToken(active=True, uid=forgot_form.user.id, email=forgot_form.email.data, expire=datetime.utcnow() + timedelta(days=1))
            db.session.add(token)
            db.session.commit()
            url = url_for("users.reset", code=token.token, _external=True)
            send_email(forgot_form.email.data, "SASE UMN Account Password Reset", "Click here to reset your password: %s" % url)
        flash("If you have an email registered with us, then you should have received an email. Check your inbox now!", "success")
        return redirect(url_for("users.forgot"))
    return render_template("users/forgot.j2", forgot_form=forgot_form)


@blueprint.route("/password/reset/<string:code>", methods=["GET", "POST"])
def reset(code):
    token = PasswordResetToken.query.filter_by(token=code, active=True).first()
    if not token or token.expired or token.email != token.user.email:
        abort(404)

    reset_form = PasswordResetForm()
    if reset_form.validate_on_submit():
        user = User.get_by_id(token.uid)
        user.password = reset_form.password.data
        token.active = False
        db.session.add(user)
        db.session.commit()
        flash("Password has been reset! Try logging in now.", "success")
        return redirect(url_for("users.login"))
    return render_template("users/reset.j2", reset_form=reset_form)


@blueprint.route("/profile")
def profile():
    return "Profile"


@blueprint.route("/settings")
def settings():
    return "Settings"


@blueprint.route("/verify/<token>")
def verify(token):
    user = User.query.filter_by(email_verification_token=token).first()
    if user:
        if user.email_verified:
            flash("Email is already verified.", "info")
            return redirect(url_for("base.index"))
        if user.email_verification_token == token:
            user.email_verified = True
            flash("Email has been verified!", "success")
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("base.index"))

    flash("Invalid token.", "danger")
    return redirect(url_for("users.login"))


def register_user(name, email, username, password, admin=False, **kwargs):
    new_user = User(name=name, username=username,
                    password=password, email=email, admin=admin)

    for key, value in kwargs.items():
        setattr(new_user, key, value)
    code = random_string()
    new_user.email_verification_token = code
    send_verification_email(username, email, url_for(
        "users.verify", token=code, _external=True))
    db.session.add(new_user)
    db.session.commit()

    return new_user


def send_verification_email(username, email, link):
    subject = "[ACTION REQUIRED] Email Verification for SASE Account."
    body = string.Template(email_template).substitute(
        link=link,
        username=username,
    )
    send_email(email, subject, body)


class LoginForm(FlaskForm):
    username = StringField("Username or Email", validators=[InputRequired("Please enter your username or email.")])
    password = PasswordField("Password", validators=[InputRequired("Please enter your password.")])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")

    def get_user(self):
        query = User.query.filter(or_(func.lower(User.username) == self.username.data.lower(),
                                      func.lower(User.email) == self.username.data.lower()))
        return query.first()

    def validate_username(self, field):
        if self.get_user() is None:
            raise ValidationError("This user doesn't exist.")

    def validate_password(self, field):
        user = self.get_user()
        if not user:
            return
        if not user.check_password(field.data):
            raise ValidationError("Check your password again.")


class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired("Please enter a name.")])
    username = StringField("Username", validators=[InputRequired("Please enter a username."), Length(3, 24, "Your username must be between 3 and 24 characters long.")])
    email = StringField("Email", validators=[InputRequired("Please enter an email."), Email("Please enter a valid email.")])
    password = PasswordField("Password", validators=[InputRequired("Please enter a password.")])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired("Please confirm your password."), EqualTo("password", "Please enter the same password.")])
    submit = SubmitField("Register")

    def validate_username(self, field):
        if not VALID_USERNAME.match(field.data):
            raise ValidationError(
                "Username must be contain letters, numbers, or _, and not start with a number.")
        if User.query.filter(func.lower(User.username) == field.data.lower()).count():
            raise ValidationError("Username is taken.")

    def validate_email(self, field):
        if User.query.filter(func.lower(User.email) == field.data.lower()).count():
            raise ValidationError("Email is taken.")


class PasswordForgotForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired("Please enter your email."), Email("Please enter a valid email.")])
    submit = SubmitField("Send Recovery Email")

    def __init__(self):
        super(PasswordForgotForm, self).__init__()
        self._user = None
        self._user_cached = False

    @property
    def user(self):
        if not self._user_cached:
            self._user = User.query.filter(func.lower(User.email) == self.email.data.lower()).first()
            self._user_cached = True
        return self._user


class PasswordResetForm(FlaskForm):
    password = PasswordField("Password", validators=[InputRequired("Please enter a password.")])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired("Please confirm your password."), EqualTo("password", "Please enter the same password.")])
    submit = SubmitField("Change Password")
