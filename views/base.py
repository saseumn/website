from flask import Blueprint, render_template

blueprint = Blueprint("base", __name__)


@blueprint.route("/")
def index():
    return render_template("base/index.j2")

@blueprint.route("/sanity")
def sanity():
    return "im sane"