from datetime import datetime, timedelta

from flask import Blueprint, render_template
from sqlalchemy import and_

from models import Event

blueprint = Blueprint("base", __name__)


@blueprint.route("/")
def index():
    upcoming = Event.query.filter(and_(Event.published == True, Event.start_time > datetime.now())).order_by(Event.start_time).first()
    return render_template("base/index.j2", upcoming=upcoming)


@blueprint.route("/about")
def about():
    return render_template("base/about.j2")


@blueprint.route("/events")
def events():
    upcoming = Event.query.filter(and_(Event.published == True, Event.start_time > datetime.now())).order_by(Event.start_time).first()
    eventlist = Event.query.filter(and_(Event.published == True, Event.start_time < datetime.now())).order_by(Event.start_time.desc()).all()
    if upcoming:
        eventlist.insert(0, upcoming)
    return render_template("base/events.j2", events=eventlist)
