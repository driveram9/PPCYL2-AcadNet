from flask import Blueprint, render_template, session, redirect, url_for, request
import os
import xml.etree.ElementTree as ET

student_bp = Blueprint("student", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
xml_path = os.path.join(BASE_DIR, "registro.xml")


@student_bp.route("/home")
def student_home():
    if session.get("rol") != "estudiante":
        return redirect(url_for("auth.login_form"))

    return render_template(
        "student/student_dashboard.html",
        nombre=session.get("usuario"),
        carnet=session.get("carnet")
    )


@student_bp.route("/courses")
def student_courses():
    if session.get("rol") != "estudiante":
        return redirect(url_for("auth.login_form"))

    cursos = []
    if os.path.exists(xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()

        carnet = session.get("carnet")

        # Buscar asignaciones de este estudiante
        asignaciones = root.find("asignaciones/c_estudiante")
        if asignaciones is not None:
            for asignacion in asignaciones.findall("estudiante_curso"):
                if asignacion.text.strip() == carnet:
                    codigo = asignacion.get("codigo")
                    # Buscar el curso con ese código
                    curso_elem = root.find("cursos").find(f"curso[@codigo='{codigo}']")
                    if curso_elem is not None:
                        cursos.append({"codigo": codigo, "nombre": curso_elem.text.strip()})

    return render_template("student/student_courses.html", cursos=cursos)


@student_bp.route("/notes")
def student_notes():
    if session.get("rol") != "estudiante":
        return redirect(url_for("auth.login_form"))

    curso_codigo = request.args.get("curso")
    notas = []

    if os.path.exists(xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Aquí podrías extender tu XML para incluir tareas/notas dentro de cada curso
        # Ejemplo: <curso codigo="770"><tarea nombre="Examen1">85</tarea></curso>
        curso_elem = root.find("cursos").find(f"curso[@codigo='{curso_codigo}']")
        if curso_elem is not None:
            for tarea in curso_elem.findall("tarea"):
                notas.append({"nombre": tarea.get("nombre"), "nota": tarea.text})

    return render_template("student/student_notes.html", curso=curso_codigo, notas=notas)
