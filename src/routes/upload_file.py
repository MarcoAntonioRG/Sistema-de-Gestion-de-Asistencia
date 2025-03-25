from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    flash,
    session,
)

from src.services.upload_file_service import *
from src.services.audit_log_service import registrar_accion

upload_file_bp = Blueprint("upload_file", __name__)


# Ruta para cargar y procesar el archivo de asistencia
@upload_file_bp.route("/api/upload", methods=["POST"])
def cargar_archivo():
    if "file" not in request.files:
        flash("No hay parte del archivo", "error")
        return redirect(url_for("asistencia.index"))

    file = request.files["file"]
    if file.filename == "":
        flash("No hay ningún archivo seleccionado", "error")
        return redirect(url_for("asistencia.index"))

    file_path = save_file(file)
    registros_validos, inconsistencias = process_file(file_path)

    try:
        registrar_accion(
            usuario="Marco Román",
            accion="Subir archivo de asistencia",
            detalles=f"Archivo: {file.filename}",
        )
    except Exception as e:
        print(f"Error registrando acción: {e}")

    # Almacena los registros válidos y las inconsistencias en la sesión para usarlos después
    session["registros_validos"] = registros_validos
    session["inconsistencias"] = inconsistencias

    if inconsistencias:
        # Renderiza la plantilla para que el usuario vea las inconsistencias
        return render_template(
            "inconsistencias.html", inconsistencias=inconsistencias, enumerate=enumerate
        )

    # Guarda registros válidos directamente si no hay inconsistencias
    guardar_registros(registros_validos)

    flash("Archivo cargado y procesado exitosamente", "success")
    return redirect(url_for("asistencia.obtener_asistencia"))
