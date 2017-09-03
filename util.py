import logging
import random
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import urljoin, urlparse

from flask import redirect, request, url_for

from config import Config

VALID_USERNAME = re.compile(r"^[A-Za-z_][A-Za-z\d_]*$")


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
    logging.error("Debug: Username={}, Password={}".format(*credentials))
    server.login(*credentials)

    msg = MIMEMultipart()
    msg["From"] = from_addr
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    server.sendmail(from_addr, recipient, msg.as_string())
