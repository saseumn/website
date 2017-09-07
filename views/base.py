from flask import Blueprint, render_template

from models import Event

blueprint = Blueprint("base", __name__)


@blueprint.route("/")
def index():
    upcoming = Event.query.filter_by(published=True).order_by(Event.start_time).first()
    return render_template("base/index.j2", upcoming=upcoming)


@blueprint.route("/about")
def about():
    return "about"


@blueprint.route("/events")
def events():
    return "events"
