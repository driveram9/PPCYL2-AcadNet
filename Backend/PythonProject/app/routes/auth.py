from flask import Blueprint, render_template, request, redirect, url_for, session
import os
import xml.etree.ElementTree as ET

auth_bp = Blueprint("auth", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
upload_folder = os.path.join(BASE_DIR, "..", "uploads")
xml_path = os.path.join(upload_folder, "registro.xml")

@auth_bp.route("/login", methods=["GET", "POST"])
def login_form():
    mensaje = None

    if request.method == "POST":
        usuario = request.form.get("usuario")
        contrasenia = request.form.get("contrasenia")

        if os.path.exists(xml_path):
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # Validar admin
            admin = root.find("admin")
            if admin is not None and admin.get("usuario") == usuario and admin.get("contrasenia") == contrasenia:
                session["rol"] = "admin"
                session["usuario"] = usuario
                return redirect(url_for("admin.admin_dashboard"))

            # Validar tutores
            for tutor in root.findall("tutores/tutor"):
                if tutor.get("registro_personal") == usuario and tutor.get("contrasenia") == contrasenia:
                    session["rol"] = "tutor"
                    session["usuario"] = tutor.text.strip()
                    return redirect(url_for("student.student_home"))

            # Validar estudiantes
            for estudiante in root.findall("estudiantes/estudiante"):
                if estudiante.get("carnet") == usuario and estudiante.get("contrasenia") == contrasenia:
                    session["rol"] = "estudiante"
                    session["usuario"] = estudiante.text.strip()  # nombre
                    session["carnet"] = estudiante.get("carnet")  # carnet del XML
                    return redirect(url_for("student.student_home"))

        mensaje = "Usuario o contraseña incorrectos"

    return render_template("login.html", mensaje=mensaje)

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login_form"))
