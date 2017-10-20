import logging
import random
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps
from urllib.parse import urljoin, urlparse
import base64
import httplib2
from apiclient import discovery
from flask import abort, flash, redirect, request, url_for
from flask_login import current_user

from config import Config

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


def create_message(recipient, subject, body, from_addr):
    message = MIMEText(body)
    message["to"] = recipient
    message["from"] = from_addr
    message["subject"] = subject
    return dict(raw=base64.urlsafe_b64encode(message.as_string()))


def send_email(recipient, subject, body, from_addr="sasemail@umn.edu"):
    # server = smtplib.SMTP("smtp.gmail.com", 587)
    # server.starttls()
    # server.login(*credentials)

    # msg = MIMEMultipart()
    # msg["From"] = from_addr
    # msg["To"] = recipient
    # msg["Subject"] = subject
    # msg.attach(MIMEText(body, "plain"))
    # server.sendmail(from_addr, recipient, msg.as_string())

    message = create_message(recipient, subject, body, from_addr)

    credentials = Config.get_email_credentials()
    if not credentials:
        return  # TODO don't fail silently.
    http = credentials.authorize(httplib2.Http())
    service = discovery.build("gmail", "v1", http=http)

    result = service.users().messages().send(userId=from_addr, message=message).execute()
    return result
