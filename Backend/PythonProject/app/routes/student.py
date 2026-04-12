from flask import Blueprint, render_template, session, redirect, url_for

student_bp = Blueprint("student", __name__)

@student_bp.route("/")
def student_home():
    # Verificar que el usuario esté logueado como estudiante
    if "rol" not in session or session["rol"] != "estudiante":
        return redirect(url_for("auth.login_form"))

    nombre = session.get("usuario", "Desconocido")
    carnet = session.get("carnet", "N/A")

    # Renderizamos la plantilla student.html
    return render_template("student.html", nombre=nombre, carnet=carnet)
