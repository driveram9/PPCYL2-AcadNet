from flask import Blueprint, jsonify

reports_bp = Blueprint("reports", __name__)

@reports_bp.route("/report", methods=["GET"])
def report():
    # Aquí podrías generar un reporte real
    datos = {
        "usuarios": 10,
        "uploads": 5,
        "errores": 1
    }
    return jsonify(datos)
