from src.extensions import db
from datetime import datetime, timezone


class Asistencia(db.Model):

    __tablename__ = "asistencia"

    id = db.Column(db.Integer, primary_key=True)
    id_reloj = db.Column(db.String(50), nullable=False)
    tipo_marcaje = db.Column(
        db.Integer, nullable=False
    )  # 1 para entrada, 3 para salida
    id_empleado = db.Column(db.String(255), nullable=False)  # ID encriptado
    hora = db.Column(db.Integer, nullable=False)
    minuto = db.Column(db.Integer, nullable=False)
    dia = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Registro de Asistencia {self.employee_id} - {self.entry_type}>"
    
    def to_dict(self):
        return {
            "id_reloj": self.id_reloj,
            "tipo_marcaje": self.tipo_marcaje,
            "id_empleado": self.id_empleado,
            "hora": self.hora,
            "minuto": self.minuto,
            "dia": self.dia,
            "mes": self.mes,
            "anio": self.anio
        }
