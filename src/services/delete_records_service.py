from src.models.asistencia import Asistencia
from src.extensions import db


def delete_all():
    try:
        # Eliminar todos los registros
        db.session.query(Asistencia).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Si ocurre un error, se revierte la transacción
        raise e
