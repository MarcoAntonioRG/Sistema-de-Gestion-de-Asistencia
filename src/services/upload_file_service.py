from src.models.asistencia import Asistencia
from src.extensions import db
from werkzeug.utils import secure_filename
from collections import defaultdict
from datetime import datetime


def save_file(file):
    """Guarda el archivo en el sistema de archivos."""
    filename = secure_filename(file.filename)
    file_path = f"./data/{filename}"
    file.save(file_path)
    return file_path

def process_file(file_path):
    registros_validos = []
    inconsistencias = []

    # Agrupar los registros por fecha y trabajador
    registros_por_fecha_empleado = defaultdict(lambda: defaultdict(list))

    with open(file_path, "r") as file:
        for line in file:
            columns = line.strip().split(",")
            if len(columns) >= 10:
                registro = crear_registro(columns)
                fecha = f"{registro['dia']}/{registro['mes']}/{registro['anio']}"
                registros_por_fecha_empleado[fecha][registro["id_empleado"]].append(
                    registro
                )

    # Procesar cada fecha y trabajador
    for fecha, registros_por_trabajador in registros_por_fecha_empleado.items():
        for id_empleado, registros_dia in registros_por_trabajador.items():
            # Separar registros por tipo de marcaje
            entradas = [r for r in registros_dia if r["tipo_marcaje"] == 1]
            salidas = [r for r in registros_dia if r["tipo_marcaje"] == 3]

            # Caso 1: Entradas duplicadas
            if len(entradas) > 1:
                inconsistencias.append(
                    {
                        "id_empleado": id_empleado,
                        "fecha": fecha,
                        "tipo_inconsistencia": "entradas_a_revisar",
                        "duplicados": entradas,
                    }
                )

            # Caso 2: Salidas duplicadas
            if len(salidas) > 1:
                inconsistencias.append(
                    {
                        "id_empleado": id_empleado,
                        "fecha": fecha,
                        "tipo_inconsistencia": "salidas_a_revisar",
                        "duplicados": salidas,
                    }
                )

            # Caso 3: Entrada sin salida en un día
            if len(entradas) == 1 and len(salidas) == 0:
                inconsistencias.append(
                    {
                        "id_empleado": id_empleado,
                        "fecha": fecha,
                        "tipo_inconsistencia": "falta_salida",
                        "entrada_faltante": entradas[0],
                    }
                )

            # Caso 4: Salida sin entrada en un día
            if len(salidas) == 1 and len(entradas) == 0:
                inconsistencias.append(
                    {
                        "id_empleado": id_empleado,
                        "fecha": fecha,
                        "tipo_inconsistencia": "falta_entrada",
                        "salida_faltante": salidas[0],
                    }
                )

            # Caso válido: Una entrada y una salida en el mismo día
            if len(entradas) == 1 and len(salidas) == 1:
                registros_validos.extend(entradas + salidas)

    return registros_validos, inconsistencias


def crear_registro(columns):
    id_reloj = columns[0]
    tipo_marcaje = int(columns[2])
    id_empleado = columns[3]
    hora = int(columns[5])
    minuto = int(columns[6])
    dia = int(columns[8])
    mes = int(columns[7])
    anio = int(columns[9])

    if anio < 100:
        anio += 2000

    return {
        "id_reloj": id_reloj,
        "tipo_marcaje": tipo_marcaje,
        "id_empleado": id_empleado,
        "hora": hora,
        "minuto": minuto,
        "dia": dia,
        "mes": mes,
        "anio": anio,
    }


def es_mismo_dia_y_empleado(registro1, registro2):
    return (
        registro1["id_empleado"] == registro2["id_empleado"]
        and registro1["dia"] == registro2["dia"]
        and registro1["mes"] == registro2["mes"]
        and registro1["anio"] == registro2["anio"]
    )


def guardar_registros(registros):
    for registro in registros:

        # Validar la estructura del registro
        campos_necesarios = ["id_empleado", "dia", "mes", "anio", "tipo_marcaje", "hora", "minuto"]
        for campo in campos_necesarios:
            if campo not in registro:
                print(f"Error: El registro no tiene el campo {campo}. Registro: {registro}")
                continue

        # Verificar si el registro completo ya existe en la base de datos
        existente = Asistencia.query.filter_by(
            id_empleado=registro["id_empleado"],
            dia=registro["dia"],
            mes=registro["mes"],
            anio=registro["anio"],
            tipo_marcaje=registro["tipo_marcaje"],
            hora=registro["hora"],
            minuto=registro["minuto"],
        ).first()

        if existente:
            # print(
            #     f"Error: Ya existe un registro idéntico para el empleado {registro['id_empleado']} el {registro['dia']}/{registro['mes']}/{registro['anio']} a las {registro['hora']}:{registro['minuto']}."
            # )
            continue  # Si el registro ya existe, lo omites

        # Verificar si ya existe una entrada o salida para el mismo trabajador en el mismo día
        if registro["tipo_marcaje"] == 1:  # Entrada
            duplicado_entrada = Asistencia.query.filter_by(
                id_empleado=registro["id_empleado"],
                dia=registro["dia"],
                mes=registro["mes"],
                anio=registro["anio"],
                tipo_marcaje=1,
            ).first()

            if duplicado_entrada:
                print(
                    f"Error: Ya existe una entrada para el trabajador {registro['id_empleado']} el {registro['dia']}/{registro['mes']}/{registro['anio']}."
                )
                continue

        elif registro["tipo_marcaje"] == 3:  # Salida
            duplicado_salida = Asistencia.query.filter_by(
                id_empleado=registro["id_empleado"],
                dia=registro["dia"],
                mes=registro["mes"],
                anio=registro["anio"],
                tipo_marcaje=3,
            ).first()

            if duplicado_salida:
                print(
                    f"Error: Ya existe una salida para el trabajador {registro['id_empleado']} el {registro['dia']}/{registro['mes']}/{registro['anio']}."
                )
                continue

        # Si no se encontró duplicado, guardar el nuevo registro
        try:
            nuevo_registro = Asistencia(**registro)
            db.session.add(nuevo_registro)
        except Exception as e:
            print(f"Error al intentar agregar el registro: {registro}. Error: {e}")

    # Commit de los registros válidos después de la verificación
    try:
        db.session.commit()
    except Exception as e:
        print(f"Error al hacer commit de los registros: {e}")


