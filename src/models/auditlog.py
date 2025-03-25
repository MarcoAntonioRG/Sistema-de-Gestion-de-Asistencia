from datetime import datetime
import pytz
from src.extensions import db

UTC = pytz.utc
LOCAL_TIMEZONE = pytz.timezone("America/Santiago")

def current_utc_time():
    return datetime.now(UTC)

class AuditLog(db.Model):
    __tablename__ = "auditlog"

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), nullable=False)  # Nombre o ID del usuario
    accion = db.Column(db.String(255), nullable=False)  # Descripción de la acción
    fecha_hora = db.Column(
        db.DateTime, default=current_utc_time
    )  # Fecha y hora del registro
    detalles = db.Column(db.Text)  # Detalles adicionales (opcional)

    def fecha_hora_local(self):
        return self.fecha_hora.astimezone(LOCAL_TIMEZONE)

    def __repr__(self):
        return f"<AuditLog {self.id} - {self.usuario} - {self.accion}>"
