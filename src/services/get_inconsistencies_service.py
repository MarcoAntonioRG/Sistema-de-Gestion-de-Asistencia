from datetime import datetime


def convertir_fecha(fecha_str):
    """Convierte una fecha en formato DD/MM/YYYY a un objeto datetime.date"""
    try:
        return datetime.strptime(fecha_str, "%d/%m/%Y").date()
    except ValueError:
        raise ValueError(f"El formato de la fecha '{fecha_str}' no es válido.")