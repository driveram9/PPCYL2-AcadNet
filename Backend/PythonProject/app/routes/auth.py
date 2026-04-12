from flask import Blueprint, request, render_template, jsonify, redirect, url_for
import xml.etree.ElementTree as ET
import os
from flask import Blueprint, request, render_template, jsonify, redirect, url_for, flash

auth_bp = Blueprint("auth", __name__)

# recolecta los datos dentro del xml
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
xml_path = os.path.join(BASE_DIR, "registro.xml")
tree = ET.parse(xml_path)
root = tree.getroot()

@auth_bp.route("/admin")
def admin_dashboard():
    return render_template("admin_dashboard.html")

@auth_bp.route("/login", methods=["GET"])
def login_form():
    return render_template("login.html")

@auth_bp.route("/login", methods=["POST"])
def login():
    usuario = request.form.get("usuario")
    contrasenia = request.form.get("contrasenia")

    resultado = validar_admin(usuario, contrasenia) or validar_tutor(usuario, contrasenia) or validar_estudiante(usuario, contrasenia)

    if resultado:
        if resultado["tipo"] == "admin":
            return redirect(url_for("auth.admin_dashboard"))
        elif resultado["tipo"] == "tutor":
            return redirect(url_for("auth.tutor_dashboard", nombre=resultado["nombre"]))
        else:
            return redirect(url_for("auth.estudiante_dashboard", nombre=resultado["nombre"]))
    else:
        flash("No se encontraron credenciales, por favor verifique usuario y contraseña")
        return redirect(url_for("auth.login_form"))


def validar_admin(usuario, contrasenia):
    admin = root.find("admin")
    if admin is not None and admin.get("usuario") == usuario and admin.get("contrasenia") == contrasenia:
        return {"tipo": "admin", "nombre": "Administrador"}
    return None

def validar_tutor(usuario, contrasenia):
    for tutor in root.find("tutores"):
        if tutor.attrib["registro_personal"] == usuario and tutor.attrib["contrasenia"] == contrasenia:
            return {"tipo": "tutor", "nombre": tutor.text}
    return None

def validar_estudiante(usuario, contrasenia):
    for estudiante in root.find("estudiantes"):
        if estudiante.attrib["carnet"] == usuario and estudiante.attrib["contrasenia"] == contrasenia:
            return {"tipo": "estudiante", "nombre": estudiante.text}
    return None
