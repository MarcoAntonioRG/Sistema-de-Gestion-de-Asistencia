from .attendance_management import asistencia_bp
from .upload_file import upload_file_bp
from .inconsistencies import inconsistencies_bp
from .get_attendance import attendance_bp
from .delete_all_records import delete_all_records_bp
from .audit_logs import *


def register_routes(app):
    app.register_blueprint(asistencia_bp)
    app.register_blueprint(upload_file_bp)
    app.register_blueprint(inconsistencies_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(delete_all_records_bp)
    app.register_blueprint(show_audit_logs_bp)
