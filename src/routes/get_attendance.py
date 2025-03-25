from flask import (
    Blueprint,
    request,
    render_template,
    flash,
    session,
    redirect,
    url_for,
    make_response,
)

from io import StringIO

from src.services.get_attendance_service import get_attendance, generate_file

attendance_bp = Blueprint("attendance", __name__)


@attendance_bp.route("/api/get", methods=["GET"])
def obtener_asistencia():
    # Obtener parámetros de filtro
    id_trabajador = request.args.get("id_trabajador")
    fecha = request.args.get("fecha")
    hora = request.args.get("hora")

    # Verificar si existen registros de asistencia en la base de datos
    registros_totales = get_attendance()
    hay_asistencia = bool(registros_totales)  # Revisa si hay algún registro en total

    # Aplicar filtros si hay registros en la base de datos
    asistencia = []
    if hay_asistencia:
        asistencia = get_attendance(id_trabajador=id_trabajador, fecha=fecha, hora=hora)
        if not asistencia:  # Si el filtro no devuelve resultados
            flash(
                "No hay registros de asistencia para los filtros seleccionados", "info"
            )

    # Guardar los registros filtrados en la sesión
    session['asistencia'] = [registro.to_dict() for registro in asistencia]

    return render_template(
        "asistencia.html", asistencia=asistencia, hay_asistencia=hay_asistencia
    )


@attendance_bp.route("/api/export", methods=["GET"])
def exportar_asistencia():
    # Obtener los registros de asistencia filtrados desde la sesión
    asistencia = session.get("asistencia", [])

    # Si no hay asistencia, redirigir con un mensaje flash
    if not asistencia:
        flash("No hay registros de asistencia para exportar.", "info")
        return redirect(url_for("attendance.obtener_asistencia"))
    
    # Crear un archivo log en memoria
    output = StringIO(newline="\n")  # Manejo de nuevas líneas multiplataforma
    try:
        generate_file(asistencia, output)

    except Exception as e:
        flash(f"Error al generar el archivo de asistencia: {e}", "danger")
        return redirect(url_for("attendance.obtener_asistencia"))
    
    # Preparar el archivo para descarga
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=encriptado_SIRH.log'
    response.headers['Content-Type'] = 'text/plain'
    return response