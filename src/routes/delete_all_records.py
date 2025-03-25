from flask import Blueprint, jsonify

from src.services.delete_records_service import delete_all

delete_all_records_bp = Blueprint("delete_all_records", __name__)


@delete_all_records_bp.route("/api/delete_all", methods=["DELETE"])
def borrar_todo():
    try:
        delete_all()
        return jsonify({"message": "Todos los registros han sido eliminados"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
