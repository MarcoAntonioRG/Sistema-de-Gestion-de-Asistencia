from src.models.asistencia import Asistencia
from datetime import datetime


def get_attendance(id_trabajador=None, fecha=None, hora=None):
    query = Asistencia.query

    # Aplicar filtros si están presentes
    if id_trabajador:
        query = query.filter(Asistencia.id_empleado == id_trabajador)
    if fecha:
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        query = query.filter(
            Asistencia.dia == fecha_obj.day,
            Asistencia.mes == fecha_obj.month,
            Asistencia.anio == fecha_obj.year,
        )
    if hora:
        hora_obj = datetime.strptime(hora, "%H:%M").time()
        query = query.filter(
            Asistencia.hora == hora_obj.hour, Asistencia.minuto == hora_obj.minute
        )

    return query.all()

def generate_file(asistencia, output):
    for registro in asistencia:
            # Validar que el registro tenga la estructura esperada
            if not all(k in registro for k in ["id_reloj", "tipo_marcaje", "id_empleado", "hora", "minuto", "dia", "mes", "anio"]):
                raise ValueError("Registro de asistencia incompleto.")
            
            # Construir la línea del archivo según el formato requerido
            line = (
                f"{registro['id_reloj']},01,0{registro['tipo_marcaje']},{registro['id_empleado']},0000000000,"
                f"{str(registro['hora']).zfill(2)},{str(registro['minuto']).zfill(2)},"
                f"{str(registro['mes']).zfill(2)},{str(registro['dia']).zfill(2)},"
                f"{str(registro['anio'])[-2:]},00,00,00,00,00,"
                "0000000000,0000000000,    0.00,    0.00\n"
            )
            output.write(line)