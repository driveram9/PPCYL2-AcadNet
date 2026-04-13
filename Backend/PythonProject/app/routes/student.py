from flask import render_template, session, redirect, url_for, Blueprint

# Crear el Blueprint
student_bp = Blueprint("student", __name__)


@student_bp.route("/estudiante")
def estudiante_dashboard():
    # Verificar que el usuario sea estudiante
    if session.get("usuario_rol") != "estudiante":
        return redirect(url_for("index"))

    return render_template("estudiante.html",
                           usuario=session.get("usuario_nombre"),
                           rol=session.get("usuario_rol"))