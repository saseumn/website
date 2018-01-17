import logging
import random
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps
from urllib.parse import urljoin, urlparse

from flask import abort, flash, redirect, request, url_for
from flask_login import current_user

from saseumn.config import Config

VALID_USERNAME = re.compile(r"^[A-Za-z_][A-Za-z\d_]*$")

# decorators


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not (current_user.is_authenticated and current_user.admin):
            flash("You don't have permission to view this page.", "danger")
            return redirect(url_for("base.index"))
        return f(*args, **kwargs)
    return wrapper


def random_string(length=32, alpha="012346789abcdef"):
    """ Generates a random string of length length using characters from alpha. """
    characters = [random.choice(alpha) for x in range(length)]
    return "".join(characters)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def get_redirect_target():
    for target in request.values.get("next"), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


def redirect_back(endpoint, **values):
    target = request.form.get("next", url_for("users.profile"))
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)


def send_email(recipient, subject, body, from_addr="example@exmaple.org"):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    credentials = Config.get_email_credentials()
    if not credentials:
        return
    server.login(*credentials)

    msg = MIMEMultipart()
    msg["From"] = from_addr
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    server.sendmail(from_addr, recipient, msg.as_string())
