from src.models.auditlog import AuditLog
from src.extensions import db
from datetime import datetime


def registrar_accion(usuario, accion, detalles=None):
    log = AuditLog(usuario=usuario, accion=accion, detalles=detalles)
    db.session.add(log)
    db.session.commit()


def get_logs(usuario, fecha_inicio, fecha_fin):
    query = AuditLog.query

    if usuario:
        query = query.filter(AuditLog.usuario.ilike(f"%{usuario}%"))
    if fecha_inicio:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            query = query.filter(AuditLog.fecha_hora >= fecha_inicio)
        except ValueError:
            print("Formato de fecha_inicio inválido")
    if fecha_fin:
        try:
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
            query = query.filter(AuditLog.fecha_hora <= fecha_fin)
        except ValueError:
            print("Formato de fecha_fin inválido")

    logs = query.order_by(AuditLog.fecha_hora.desc()).all() or []

    return logs


def get_logs_pdf():
    logs = AuditLog.query.order_by(AuditLog.fecha_hora.desc()).all()
    return logs
