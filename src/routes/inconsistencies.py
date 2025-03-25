from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    flash,
    session,
)

from datetime import datetime

from src.services.upload_file_service import guardar_registros
from src.services.get_inconsistencies_service import convertir_fecha
from src.services.audit_log_service import registrar_accion

inconsistencies_bp = Blueprint("inconsistencies", __name__)


@inconsistencies_bp.route("/inconsistencias", methods=["GET"])
def mostrar_inconsistencias():
    # Obtener parámetros de filtro
    fecha_inicio = request.args.get("fecha_inicio")  # Formato esperado: 'YYYY-MM-DD'
    fecha_fin = request.args.get("fecha_fin")  # Formato esperado: 'YYYY-MM-DD'

    # Obtener inconsistencias almacenadas en la sesión
    inconsistencias = session.get("inconsistencias", [])

    # Filtrar inconsistencias por fecha o rango de fechas
    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        inconsistencias = [
            inc
            for inc in inconsistencias
            if convertir_fecha(inc["fecha"]) >= fecha_inicio
        ]
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        inconsistencias = [
            inc for inc in inconsistencias if convertir_fecha(inc["fecha"]) <= fecha_fin
        ]

    # Renderiza la plantilla con las inconsistencias filtradas
    return render_template(
        "inconsistencias.html", inconsistencias=inconsistencias, enumerate=enumerate
    )


@inconsistencies_bp.route("/resolve_inconsistencias", methods=["POST"])
def resolver_inconsistencias():
    # Obtener los registros válidos desde la sesión
    registros_validos = session.get("registros_validos", [])

    # Obtener todas las inconsistencias desde la sesión
    todas_inconsistencias = session.get("inconsistencias", [])
    
    # Crear un diccionario para mapear las inconsistencias por ID empleado y fecha
    inconsistencias_mapeadas = {
        (inconsistencia["id_empleado"], inconsistencia["fecha"]): inconsistencia
        for inconsistencia in todas_inconsistencias
    }

    # Acciones registradas para logs
    acciones_registradas = []

    # Procesar las entradas del formulario
    for key, value in request.form.items():
        partes = key.split("_")
        if len(partes) < 3:
            continue  # Ignorar claves no relevantes

        tipo, id_empleado, fecha = partes[0], partes[2], partes[3]
        inconsistencia = inconsistencias_mapeadas.get((id_empleado, fecha))

        if inconsistencia:
            detalles_accion = f"Acciones realizadas:"

            # Procesar entradas o salidas duplicadas
            if inconsistencia["tipo_inconsistencia"] == "entradas_a_revisar" or inconsistencia["tipo_inconsistencia"] == "salidas_a_revisar":
                duplicados = inconsistencia["duplicados"]
                accion, idx = value.split("_")
                idx = int(idx)
                registro = duplicados[idx]

                if accion == "conservar":
                    registros_validos.append(registro)
                    detalles_accion += (
                        f" Conservar {tipo} para empleado {registro['id_empleado']} "
                        f"en reloj {registro['id_reloj']} a las {registro['hora']}:{registro['minuto']} hrs, "
                        f"el dia {registro['dia']}/{registro['mes']}/{registro['anio']}."
                    )

                elif accion == "convertir":
                    registro_convertido = registro.copy()
                    if tipo == "entrada":
                        registro_convertido["tipo_marcaje"] = 3  # Convertir a salida
                        detalles_accion += (
                            f" Convertir entrada a salida para empleado {registro['id_empleado']} "
                            f"en reloj {registro['id_reloj']} a las {registro['hora']}:{registro['minuto']} hrs, "
                            f"el dia {registro['dia']}/{registro['mes']}/{registro['anio']}."
                        )
                    elif tipo == "salida":
                        registro_convertido["tipo_marcaje"] = 1  # Convertir a entrada
                        detalles_accion += (
                            f" Convertir salida a entrada para empleado {registro['id_empleado']} "
                            f"en reloj {registro['id_reloj']} a las {registro['hora']}:{registro['minuto']} hrs, "
                            f"el dia {registro['dia']}/{registro['mes']}/{registro['anio']}."
                        )
                    registros_validos.append(registro_convertido)

            # Procesar salidas faltantes
            elif inconsistencia["tipo_inconsistencia"] == "falta_salida":
                entrada_faltante = inconsistencia.get("entrada_faltante")
                salida_definida = request.form.get(
                    f"salida_definida_{id_empleado}_{fecha}"
                )
                if entrada_faltante and salida_definida:
                    hora, minuto = map(int, salida_definida.split(":"))
                    # Crear un registro de salida con los datos definidos por el usuario
                    registro_salida = {
                        "id_reloj": entrada_faltante["id_reloj"],
                        "tipo_marcaje": 3,
                        "id_empleado": id_empleado,
                        "hora": hora,
                        "minuto": minuto,
                        "dia": entrada_faltante["dia"],
                        "mes": entrada_faltante["mes"],
                        "anio": entrada_faltante["anio"],
                    }
                    registros_validos.append(entrada_faltante)
                    registros_validos.append(registro_salida)
                    detalles_accion += (
                        f" Salida faltante creada para empleado {registro_salida['id_empleado']} "
                        f"en reloj {registro_salida['id_reloj']} a las {registro_salida['hora']}:{registro_salida['minuto']} hrs, "
                        f"el dia {registro_salida['dia']}/{registro_salida['mes']}/{registro_salida['anio']}."
                    )

            # Procesar entradas faltantes
            elif inconsistencia["tipo_inconsistencia"] == "falta_entrada":
                salida_faltante = inconsistencia.get("salida_faltante")
                entrada_definida = request.form.get(
                    f"entrada_definida_{id_empleado}_{fecha}"
                )
                if salida_faltante and entrada_definida:
                    hora, minuto = map(int, entrada_definida.split(":"))
                    # Crear un registro de entrada con los datos definidos por el usuario
                    registro_entrada = {
                        "id_reloj": salida_faltante["id_reloj"],
                        "tipo_marcaje": 1,
                        "id_empleado": id_empleado,
                        "hora": hora,
                        "minuto": minuto,
                        "dia": salida_faltante["dia"],
                        "mes": salida_faltante["mes"],
                        "anio": salida_faltante["anio"],
                    }
                    registros_validos.append(registro_entrada)
                    registros_validos.append(salida_faltante)
                    detalles_accion += (
                        f" Entrada faltante creada para empleado {registro_salida['id_empleado']} "
                        f"en reloj {registro_salida['id_reloj']} a las {registro_salida['hora']}:{registro_salida['minuto']} hrs, "
                        f"el dia {registro_salida['dia']}/{registro_salida['mes']}/{registro_salida['anio']}."
                    )

            # Registrar las acciones realizadas
            acciones_registradas.append(detalles_accion)

    # Guardar los registros válidos en la base de datos
    guardar_registros(registros_validos)

    # Registrar las acciones realizadas en los logs
    for accion in acciones_registradas:
        try:
            registrar_accion(
                usuario="Marco Román",
                accion="Resolver inconsistencia",
                detalles=accion,
            )
        except Exception as e:
            print(f"Error registrando acción para {accion}: {e}")

    # Limpiar la sesión
    session.pop("registros_validos", None)
    session.pop("inconsistencias", None)

    flash("Inconsistencias resueltas y guardadas", "success")
    return redirect(url_for("attendance.obtener_asistencia"))