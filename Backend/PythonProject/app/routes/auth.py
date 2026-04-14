# auth.py - Versión corregida y mejorada
from flask import Blueprint, request, jsonify
import os
import xml.etree.ElementTree as ET

auth_bp = Blueprint("auth", __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
xml_path = os.path.join(BASE_DIR, "registro.xml")

ADMIN_USUARIO = "AdminPPCYL2"
ADMIN_CONTRASENIA = "AdminPPCYL2771"
ADMIN_NOMBRE = "Administrador del Sistema"


@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    """Endpoint para login de todos los usuarios (admin, tutor, estudiante)"""
    data = request.get_json()
    usuario = data.get("usuario")
    contrasenia = data.get("contrasenia")

    print(f"🔍 Intentando login: usuario={usuario}")

    # ========================================
    # 1. VALIDAR ADMIN
    # ========================================
    if usuario == ADMIN_USUARIO and contrasenia == ADMIN_CONTRASENIA:
        return jsonify({
            "success": True,
            "rol": "admin",
            "nombre": ADMIN_NOMBRE
        }), 200

    # ========================================
    # 2. VALIDAR DESDE XML (tutores y estudiantes)
    # ========================================
    if os.path.exists(xml_path):
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # ====================================
            # Validar TUTORES
            # ====================================
            for tutor in root.findall("tutores/tutor"):
                registro = tutor.get("registro_personal")
                password = tutor.get("contrasenia")
                nombre = tutor.text.strip() if tutor.text else ""

                if registro == usuario and password == contrasenia:
                    print(f"✅ Tutor logueado: {nombre} (registro: {registro})")
                    return jsonify({
                        "success": True,
                        "rol": "tutor",
                        "nombre": nombre,
                        "registro": registro
                    }), 200

            # ====================================
            # Validar ESTUDIANTES
            # ====================================
            for estudiante in root.findall("estudiantes/estudiante"):
                carnet = estudiante.get("carnet")
                password = estudiante.get("contrasenia")
                nombre = estudiante.text.strip() if estudiante.text else ""

                if carnet == usuario and password == contrasenia:
                    print(f"✅ Estudiante logueado: {nombre} (carnet: {carnet})")
                    return jsonify({
                        "success": True,
                        "rol": "estudiante",
                        "nombre": nombre,
                        "carnet": carnet
                    }), 200

        except Exception as e:
            print(f"❌ Error al leer XML: {e}")
            return jsonify({"success": False, "mensaje": "Error en el servidor"}), 500

    # ========================================
    # 3. CREDENCIALES INCORRECTAS
    # ========================================
    print(f"❌ Login fallido para usuario: {usuario}")
    return jsonify({"success": False, "mensaje": "Credenciales incorrectas"}), 401