from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
import xml.etree.ElementTree as ET

app = Flask(__name__)
app.secret_key = "clave_super_secreta_2024"
CORS(app, origins=["http://localhost:8000", "http://127.0.0.1:8000"], supports_credentials=True)

# ============================================
# RUTAS API (DEBEN ESTAR AQUÍ O IMPORTADAS)
# ============================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
xml_path = os.path.join(BASE_DIR, "registro.xml")

print(f"📁 Buscando XML en: {xml_path}")
print(f"📁 ¿Existe? {os.path.exists(xml_path)}")

ADMIN_USUARIO = "AdminPPCYL2"
ADMIN_CONTRASENIA = "AdminPPCYL2771"
ADMIN_NOMBRE = "Administrador del Sistema"


@app.route("/api/login", methods=["POST"])
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
            for tutor in root.findall(".//tutor"):
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
            for estudiante in root.findall(".//estudiante"):
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


@app.route("/api/test", methods=["GET"])
def api_test():
    """Endpoint de prueba"""
    return jsonify({
        "status": "ok",
        "xml_path": xml_path,
        "xml_exists": os.path.exists(xml_path)
    })


@app.route("/api/horarios/<registro>", methods=["GET"])
def api_get_horarios(registro):
    """Obtener horarios de un tutor"""
    import json
    horarios_dir = os.path.join(BASE_DIR, "uploads", "horarios")
    horarios_file = os.path.join(horarios_dir, f"{registro}.json")

    if os.path.exists(horarios_file):
        with open(horarios_file, "r", encoding="utf-8") as f:
            horarios = json.load(f)
        return jsonify(horarios), 200
    return jsonify([]), 200


@app.route("/api/cursos/<registro>", methods=["GET"])
def api_get_cursos(registro):
    """Obtener cursos de un tutor"""
    cursos = []

    if os.path.exists(xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()

        for tutor_curso in root.findall("asignaciones/c_tutores/tutor_curso"):
            if tutor_curso.text == registro:
                codigo = tutor_curso.get("codigo")
                for curso in root.findall("cursos/curso"):
                    if curso.get("codigo") == codigo:
                        cursos.append({
                            "codigo": codigo,
                            "nombre": curso.text
                        })
                        break

    return jsonify(cursos), 200


# ============================================
# IMPORTAR BLUEPRINTS (si los tienes)
# ============================================
try:
    from routes.admin import admin_bp
    from routes.tutor import tutor_bp
    from routes.student import student_bp

    app.register_blueprint(admin_bp)
    app.register_blueprint(tutor_bp)
    app.register_blueprint(student_bp)
except Exception as e:
    print(f"⚠️ No se pudieron importar blueprints: {e}")

if __name__ == "__main__":
    print("\n🚀 INICIANDO SERVIDOR FLASK")
    print("=" * 50)
    print("📌 Endpoints disponibles:")
    print("   POST /api/login")
    print("   GET  /api/test")
    print("   GET  /api/horarios/<registro>")
    print("   GET  /api/cursos/<registro>")
    print("=" * 50)
    app.run(debug=True, port=5000)