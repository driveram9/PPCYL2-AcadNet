from flask import Blueprint, request, jsonify, session
import os
import xml.etree.ElementTree as ET

auth_bp = Blueprint("auth", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
upload_folder = os.path.join(BASE_DIR, "..", "uploads")
xml_path = os.path.join(upload_folder, "registro.xml")

ADMIN_USUARIO = "AdminPPCYL2"
ADMIN_CONTRASENIA = "AdminPPCYL2771"
ADMIN_NOMBRE = "Administrador del Sistema"

@auth_bp.route("/login", methods=["POST"])
def login_api():
    data = request.get_json()
    usuario = data.get("usuario")
    contrasenia = data.get("contrasenia")

    # Validar admin
    if usuario == ADMIN_USUARIO and contrasenia == ADMIN_CONTRASENIA:
        return jsonify({"status": "ok", "rol": "admin", "nombre": ADMIN_NOMBRE})

    # Validar tutores y estudiantes desde XML
    if os.path.exists(xml_path):
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            for tutor in root.findall("tutores/tutor"):
                if tutor.get("registro_personal") == usuario and tutor.get("contrasenia") == contrasenia:
                    return jsonify({
                        "status": "ok",
                        "rol": "tutor",
                        "nombre": tutor.text.strip(),
                        "registro_personal": tutor.get("registro_personal")
                    })

            for estudiante in root.findall("estudiantes/estudiante"):
                if estudiante.get("carnet") == usuario and estudiante.get("contrasenia") == contrasenia:
                    return jsonify({
                        "status": "ok",
                        "rol": "estudiante",
                        "nombre": estudiante.text.strip(),
                        "carnet": estudiante.get("carnet")
                    })

        except ET.ParseError:
            return jsonify({"status": "error", "mensaje": "Error en el archivo XML"})
        except Exception as e:
            return jsonify({"status": "error", "mensaje": str(e)})

    return jsonify({"status": "error", "mensaje": "Usuario o contraseña incorrectos"})
