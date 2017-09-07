from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, TextAreaField
from wtforms.fields.html5 import DateTimeLocalField

from models import Event, db
from util import admin_required

blueprint = Blueprint("admin", __name__)


class NotReadyForPublishException(Exception):
    pass


@blueprint.route("/events")
@login_required
@admin_required
def events():
    eventlist = Event.query.all()
    return render_template("admin/events/index.j2", events=eventlist)


@blueprint.route("/events/new", methods=["GET", "POST"])
@login_required
@admin_required
def events_new():
    new_event_form = NewEventForm()
    if new_event_form.validate_on_submit():
        evt = Event()
        evt.name = new_event_form.name.data
        db.session.add(evt)
        db.session.commit()
        flash("Event created!", "success")
        return redirect(url_for("admin.events"))
    return render_template("admin/events/new.j2", new_event_form=new_event_form)


@blueprint.route("/events/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def events_edit(id):
    event = Event.query.filter_by(id=id).first()
    publishable = False
    if not event.published:
        publishable = True
    if not event:
        return abort(404)
    event_edit_form = EventEditForm()
    if event_edit_form.validate_on_submit():
        event.name = event_edit_form.name.data
        event.location = event_edit_form.location.data
        event.description = event_edit_form.description.data
        event.start_time = event_edit_form.start_time.data
        if event_edit_form.update.data == True:
            db.session.add(event)
            db.session.commit()
            flash("Event updated!", "success")
            return redirect(url_for("admin.events_edit", id=id))
        elif event_edit_form.publish.data == True:
            # validation
            try:
                if not(event.name and event.location and event.description):
                    raise NotReadyForPublishException("")
            except NotReadyForPublishException as e:
                flash(e.message, "danger")
            else:
                event.published = True
                db.session.add(event)
                db.session.commit()
                flash("Event published!", "success")
                return redirect(url_for("admin.events"))
        elif event_edit_form.unpublish.data == True:
            event.published = False
            db.session.add(event)
            db.session.commit()
            return redirect(url_for("admin.events"))
    elif not event_edit_form.errors:
        event_edit_form.name.data = event.name
        event_edit_form.location.data = event.location
        event_edit_form.description.data = event.description
        event_edit_form.start_time.data = event.start_time
    return render_template("admin/events/edit.j2", event=event, event_edit_form=event_edit_form)


@blueprint.route("/events/delete/<int:id>")
@login_required
@admin_required
def events_delete(id):
    event = Event.query.filter_by(id=id).first()
    if not event:
        return abort(404)
    db.session.delete(event)
    db.session.commit()
    flash("Event removed.", "success")
    return redirect(url_for("admin.events"))


@blueprint.route("/settings")
def settings():
    return render_template("admin/settings.j2")


class NewEventForm(FlaskForm):
    name = StringField("Event Name")
    submit = SubmitField("Create Event")


class EventEditForm(FlaskForm):
    name = StringField("Event Name")
    location = StringField("Location")
    description = TextAreaField("Description")
    start_time = DateTimeLocalField("Start Time", format='%Y-%m-%dT%H:%M')
    update = SubmitField("Update Event")
    publish = SubmitField("Publish Event")
    unpublish = SubmitField("Unpublish Event")
