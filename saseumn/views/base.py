from datetime import datetime, timedelta

from flask import Blueprint, render_template
from sqlalchemy import and_

from saseumn.models import Event

blueprint = Blueprint("base", __name__)


@blueprint.route("/")
def index():
    upcoming = Event.query.filter(and_(Event.published, Event.start_time > datetime.now())).order_by(Event.start_time).first()
    return render_template("base/index.html", upcoming=upcoming)


@blueprint.route("/about")
def about():
    # team = [
    #     {
    #         'avatar': '/static/img/dev.jpg',
    #         'username': 'Dist',
    #         'name': 'Devin Deng',
    #         'role': 'Webmaster',
    #         'website': 'example'
    #     },
    #     {
    #         'username': 'michael',
    #         'name': 'Michael Zhang',
    #         'role': 'Webmaster',
    #         'website': 'example'
    #     }
    # ]
    return render_template("base/about.html")


@blueprint.route("/events")
def events():
    upcoming = Event.query.filter(and_(Event.published, Event.start_time > datetime.now())).order_by(Event.start_time).first()
    eventlist = Event.query.filter(and_(Event.published, Event.start_time < datetime.now())).order_by(Event.start_time.desc()).all()
    if upcoming:
        eventlist.insert(0, upcoming)
    return render_template("base/events.html", events=eventlist)
