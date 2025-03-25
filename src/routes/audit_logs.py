from flask import Blueprint, render_template, request, make_response, jsonify
from src.services.audit_log_service import *

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import pytz

show_audit_logs_bp = Blueprint("show_audit_logs", __name__)


@show_audit_logs_bp.route("/audit-log", methods=["GET"])
def show_audit_log():
    usuario = request.args.get("usuario")
    fecha_inicio = request.args.get("fecha_inicio")
    fecha_fin = request.args.get("fecha_fin")

    logs = get_logs(usuario, fecha_inicio, fecha_fin)

    # Debug: Imprimir los logs para verificar
    # print("Logs obtenidos:", logs)

    logs_with_index = [(idx, log) for idx, log in enumerate(logs, start=1)]
    return render_template("audit_log.html", logs_with_index=logs_with_index)

@show_audit_logs_bp.route("/audit-log/pdf", methods=["GET"])
def show_audit_log_pdf():
    try:
        # Crear un buffer para el PDF
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        pdf.setFont("Helvetica", 12)

        # Generar nombre del archivo con fecha y hora usando la zona horaria
        tz = pytz.timezone('America/Santiago')
        file_name = f"Reporte_de_Auditoria_{datetime.now(tz).strftime('%Y-%m-%d_%H-%M-%S')}.pdf"

        # Título del PDF
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(200, 750, "Reporte de Auditoría - Hospital")

        # Fecha y hora del reporte
        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, 720, "Fecha y Hora del Reporte:")
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(200, 720, datetime.now(tz).strftime("%Y-%m-%d %H:%M"))

        y_position = 680

        logs = get_logs_pdf()

        # Agregar los logs con ajuste de texto
        pdf.setFont("Helvetica-Bold", 10)
        for log in logs:
            if y_position < 50:  # Si la posición Y es muy baja, agregar una nueva página
                pdf.showPage()
                pdf.setFont("Helvetica-Bold", 10)
                pdf.drawString(50, 750, "Usuario:")
                pdf.drawString(150, 750, "Acción:")
                pdf.drawString(250, 750, "Detalles:")
                pdf.drawString(400, 750, "Fecha y Hora:")
                y_position = 730

            # Agregar cada campo en una sola línea, usando el espacio disponible
            text = f"Usuario: {log.usuario}   Acción: {log.accion}   Detalles: {log.detalles}   Fecha y Hora: {log.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Usar textobject para agregar texto largo
            text_object = pdf.beginText(50, y_position)
            text_object.setFont("Helvetica", 10)
            text_object.setTextOrigin(50, y_position)
            text_object.setLeading(12)  # Espaciado entre líneas

            # Dividir el texto en líneas si es muy largo para ajustarse
            max_line_length = 100
            lines = [text[i:i+max_line_length] for i in range(0, len(text), max_line_length)]
            for line in lines:
                text_object.textLine(line)

            pdf.drawText(text_object)

            # Ajustar la posición para agregar un salto de línea después de cada log
            y_position -= 12 * len(lines)  # Ajustar el espacio dependiendo del número de líneas
            y_position -= 12  # Agregar un salto de línea extra entre logs

        # Guardar el PDF en el buffer
        pdf.save()
        buffer.seek(0)

        # Configurar la respuesta
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{file_name}"; filename*=UTF-8\'\'{file_name}'

        # Evitar caché
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

        return response
    
    except Exception as e:
        print("Error al generar el reporte:", str(e))
        return jsonify({"error": str(e)}), 500
