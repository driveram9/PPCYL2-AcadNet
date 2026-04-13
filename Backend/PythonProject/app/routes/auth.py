from flask import Blueprint, request, jsonify, session
from flask_cors import CORS
import os
import xml.etree.ElementTree as ET

auth_bp = Blueprint("auth", __name__)

# ============================================
# CORREGIR RUTA DEL XML
# ============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Opción 1: XML en la misma carpeta que app.py
#xml_path = os.path.join(BASE_DIR, "..", "registro.xml")

# Opción 2: XML en carpeta uploads (crear si no existe)
#xml_path = os.path.join(BASE_DIR, "..", "uploads", "registro.xml")

# Opción 3: Ruta absoluta (más segura)
xml_path = r"C:\Users\PCAAE\PycharmProjects\PPCYL2-AcadNet\Backend\PythonProject\registro.xml"

print(f"📁 Buscando XML en: {xml_path}")
print(f"📁 ¿Existe? {os.path.exists(xml_path)}")

# Credenciales admin
ADMIN_USUARIO = "AdminPPCYL2"
ADMIN_CONTRASENIA = "AdminPPCYL2771"
ADMIN_NOMBRE = "Administrador del Sistema"


@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    """Endpoint para que Django consulte"""
    data = request.get_json()
    usuario = data.get("usuario")
    contrasenia = data.get("contrasenia")

    print(f"🔍 Intentando login: usuario={usuario}")

    # Validar admin
    if usuario == ADMIN_USUARIO and contrasenia == ADMIN_CONTRASENIA:
        print(f"✅ Admin logueado: {usuario}")
        return jsonify({
            "success": True,
            "rol": "admin",
            "nombre": ADMIN_NOMBRE
        }), 200

    # Validar desde XML
    if os.path.exists(xml_path):
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            print("📌 Buscando en XML...")

            # Validar tutores
            for tutor in root.findall("tutores/tutor"):
                registro = tutor.get("registro_personal")
                password = tutor.get("contrasenia")
                nombre = tutor.text.strip() if tutor.text else ""

                print(f"   Comparando tutor: {registro} vs {usuario}")

                if registro == usuario and password == contrasenia:
                    print(f"✅ Tutor encontrado: {nombre}")
                    return jsonify({
                        "success": True,
                        "rol": "tutor",
                        "nombre": nombre
                    }), 200

            # Validar estudiantes
            for estudiante in root.findall("estudiantes/estudiante"):
                carnet = estudiante.get("carnet")
                password = estudiante.get("contrasenia")
                nombre = estudiante.text.strip() if estudiante.text else ""

                print(f"   Comparando estudiante: {carnet} vs {usuario}")

                if carnet == usuario and password == contrasenia:
                    print(f"✅ Estudiante encontrado: {nombre}")
                    return jsonify({
                        "success": True,
                        "rol": "estudiante",
                        "nombre": nombre
                    }), 200

        except Exception as e:
            print(f"❌ Error al leer XML: {e}")
            return jsonify({"success": False, "mensaje": f"Error en servidor: {e}"}), 500
    else:
        print(f"❌ XML no encontrado en: {xml_path}")
        return jsonify({"success": False, "mensaje": "Archivo de datos no encontrado"}), 404

    print(f"❌ Credenciales incorrectas para: {usuario}")
    return jsonify({"success": False, "mensaje": "Credenciales incorrectas"}), 401