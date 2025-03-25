from flask import Blueprint, render_template

asistencia_bp = Blueprint("asistencia", __name__)


@asistencia_bp.route("/")
def index():
    return render_template("index.html")
