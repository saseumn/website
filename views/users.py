from flask import Blueprint, render_template
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.fields import (BooleanField, PasswordField, StringField,
                            SubmitField)
from wtforms.validators import InputRequired

from models import User
from util import get_redirect_target

blueprint = Blueprint("users", __name__, template_folder="templates")


@blueprint.route("/login", methods=["GET", "POST"])
def login():
    redirect_to = get_redirect_target()
    if current_user.is_authenticated:
        return redirect_back("users.profile")
    login_form = LoginForm(remember=True)
    if login_form.validate_on_submit():
        user = login_form.get_user()
        if not user.admin and (get_require_email_verification() and not user.email_verified):
            flash("You haven't activated your account yet! Check your email for an activation email.", "danger")
            return redirect(url_for("users.login"))
        login_user(user)
        flash("Successfully logged in!", "success")
        return redirect_back("users.profile")
    return render_template("users/login.j2", login_form=login_form, next=redirect_to)


@blueprint.route("/logout")
def logout():
    logout_user()
    flash("Successfully logged out!", "success")
    return redirect(url_for("base.index"))


@blueprint.route("/register", methods=["GET", "POST"])
def register():
    register_form = RegisterForm(prefix="register")
    if register_form.validate_on_submit():
        send_email = True  # TODO
        new_user = register_user(register_form.name.data,
                                 register_form.email.data,
                                 register_form.username.data,
                                 register_form.password.data,
                                 int(register_form.level.data),
                                 send_email=send_email, admin=False)

        if send_email:
            flash("Check your email for an activation link.", "info")
            return redirect(url_for("users.login"))

        login_user(new_user)
        return redirect(url_for("users.profile"))
    return render_template("users/register.j2", register_form=register_form)


@blueprint.route("/forgot")
def forgot():
    return "Forgot"


def register_user(name, email, username, password, level, admin=False, send_email=True, **kwargs):
    new_user = User(name=name, username=username, password=password, email=email, admin=admin)

    for key, value in kwargs.items():
        setattr(new_user, key, value)
    code = random_string()
    new_user.email_verification_token = code
    if send_email:
        send_verification_email(username, email, url_for("users.verify", token=code, _external=True))
    db.session.add(new_user)
    db.session.commit()

    return new_user


def send_verification_email(username, email, link):
    subject = "[ACTION REQUIRED] Email Verification - {}".format(ctf_name)
    body = string.Template(Config.get("email_body")).substitute(
        ctf_name=ctf_name,
        link=link,
        username=username,
    )
    response = send_email(email, subject, body)
    if response.status_code != 200:
        raise Exception("Failed: {}".format(response.text))
    response = response.json()
    if "Queued" in response["message"]:
        return True
    else:
        raise Exception(response["message"])


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired("Please enter your username.")])
    password = PasswordField("Password", validators=[InputRequired("Please enter your password.")])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")

    def get_user(self):
        query = User.query.filter(func.lower(User.username) == self.username.data.lower())
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
