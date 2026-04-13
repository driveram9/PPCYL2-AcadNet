from flask import Blueprint, render_template, request, redirect, url_for, session
import os
import xml.etree.ElementTree as ET

auth_bp = Blueprint("auth", __name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
xml_path = os.path.join(BASE_DIR, "registro.xml")

# ============================================
# CREDENCIALES DEL ADMIN (dentro del código)
# ============================================
ADMIN_USUARIO = "AdminPPCYL2"
ADMIN_CONTRASENIA = "AdminPPCYL2771"
ADMIN_NOMBRE = "Administrador del Sistema"


@auth_bp.route("/login", methods=["GET", "POST"])
def login_form():
    mensaje = None

    if request.method == "POST":
        usuario = request.form.get("usuario")
        contrasenia = request.form.get("contrasenia")
        print(f"Intento de login: usuario={usuario}, contrasenia={contrasenia}")

        # ========================================
        # 1. VALIDAR ADMIN (desde el código)
        # ========================================
        if usuario == ADMIN_USUARIO and contrasenia == ADMIN_CONTRASENIA:
            session["rol"] = "admin"
            session["usuario"] = ADMIN_NOMBRE
            session["login"] = usuario
            print(f"✅ Admin logueado: {usuario}")
            return redirect(url_for("admin.admin_dashboard"))

        # ========================================
        # 2. VALIDAR DESDE XML (tutores y estudiantes)
        # ========================================
        if os.path.exists(xml_path):
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()  # raíz = <configuraciones>

                # Validar tutores
                tutores = root.find("tutores")
                if tutores is not None:
                    for tutor in tutores.findall("tutor"):
                        print(f"🔎 Tutor encontrado: registro={tutor.get('registro_personal')}, contrasenia={tutor.get('contrasenia')}")
                        if tutor.get("registro_personal") == usuario and tutor.get("contrasenia") == contrasenia:
                            session["rol"] = "tutor"
                            session["usuario"] = tutor.text.strip()
                            session["registro_personal"] = tutor.get("registro_personal")
                            print(f"✅ Tutor logueado: {tutor.text.strip()}")
                            return redirect(url_for("student.student_home"))

                # Validar estudiantes
                estudiantes = root.find("estudiantes")
                if estudiantes is not None:
                    for estudiante in estudiantes.findall("estudiante"):
                        print(f"🔎 Estudiante encontrado: carnet={estudiante.get('carnet')}, contrasenia={estudiante.get('contrasenia')}, nombre={estudiante.text.strip()}")
                        if estudiante.get("carnet") == usuario and estudiante.get("contrasenia") == contrasenia:
                            session["rol"] = "estudiante"
                            session["usuario"] = estudiante.text.strip()
                            session["carnet"] = estudiante.get("carnet")
                            print(f"✅ Estudiante logueado: {estudiante.text.strip()}")
                            return redirect(url_for("student.student_home"))

            except ET.ParseError:
                print("❌ Error al parsear el archivo XML")
                mensaje = "Error en el archivo de datos"
            except Exception as e:
                print(f"❌ Error inesperado: {e}")
                mensaje = "Error al procesar los datos"
        else:
            print(f"⚠️ Archivo XML no encontrado en: {xml_path}")
            mensaje = "Error: Archivo de datos no encontrado"

        # Si llegamos aquí, las credenciales son incorrectas
        mensaje = "❌ Usuario o contraseña incorrectos"

    return render_template("login.html", mensaje=mensaje)


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login_form"))
