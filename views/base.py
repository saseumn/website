from datetime import datetime, timedelta

from flask import Blueprint, render_template
from sqlalchemy import and_

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
    eventlist = Event.query.filter(and_(Event.published is True, Event.start_time < (datetime.now() + timedelta(seconds=1)))).order_by(Event.start_time.desc()).all()
    return render_template("base/events.j2", events=eventlist)
