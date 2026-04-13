# auth.py - Versión corregida
from flask import Blueprint, request, jsonify
import os
import xml.etree.ElementTree as ET

auth_bp = Blueprint("auth", __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
xml_path = os.path.join(BASE_DIR, "registro.xml")

ADMIN_USUARIO = "AdminPPCYL2"
ADMIN_CONTRASENIA = "AdminPPCYL2771"
ADMIN_NOMBRE = "Administrador del Sistema"


@auth_bp.route("/api/login", methods=["POST"])  # ← IMPORTANTE: la ruta completa es /api/login
def api_login():
    data = request.get_json()
    usuario = data.get("usuario")
    contrasenia = data.get("contrasenia")

    print(f"🔍 Intentando login: usuario={usuario}")

    # Validar admin
    if usuario == ADMIN_USUARIO and contrasenia == ADMIN_CONTRASENIA:
        return jsonify({"success": True, "rol": "admin", "nombre": ADMIN_NOMBRE}), 200

    # Validar desde XML
    if os.path.exists(xml_path):
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            for tutor in root.findall(".//tutor"):
                if tutor.get("registro_personal") == usuario and tutor.get("contrasenia") == contrasenia:
                    return jsonify({"success": True, "rol": "tutor", "nombre": tutor.text.strip()}), 200

            for estudiante in root.findall(".//estudiante"):
                if estudiante.get("carnet") == usuario and estudiante.get("contrasenia") == contrasenia:
                    return jsonify({"success": True, "rol": "estudiante", "nombre": estudiante.text.strip()}), 200
        except Exception as e:
            print(f"Error: {e}")

    return jsonify({"success": False, "mensaje": "Credenciales incorrectas"}), 401