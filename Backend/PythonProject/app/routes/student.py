from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
import os
import xml.etree.ElementTree as ET
import requests

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

        asignaciones = root.find("asignaciones/c_estudiante")
        if asignaciones is not None:
            for asignacion in asignaciones.findall("estudiante_curso"):
                if asignacion.text.strip() == carnet:
                    codigo = asignacion.get("codigo")
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

        curso_elem = root.find("cursos").find(f"curso[@codigo='{curso_codigo}']")
        if curso_elem is not None:
            for tarea in curso_elem.findall("tarea"):
                notas.append({"nombre": tarea.get("nombre"), "nota": tarea.text})

    return render_template("student/student_notes.html", curso=curso_codigo, notas=notas)


# ============================================
# API RUTAS PARA ESTUDIANTE (CONSULTAR DATOS)
# ============================================

@student_bp.route("/api/estudiante/cursos", methods=["GET"])
def api_estudiante_cursos():
    """API para obtener cursos del estudiante"""
    if session.get("rol") != "estudiante":
        return jsonify({"error": "No autorizado"}), 403

    carnet = session.get("carnet")
    cursos = []

    if os.path.exists(xml_path):
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            for ec in root.findall("asignaciones/c_estudiante/estudiante_curso"):
                if ec.text == carnet:
                    codigo_curso = ec.get("codigo")
                    for curso in root.findall("cursos/curso"):
                        if curso.get("codigo") == codigo_curso:
                            cursos.append({
                                "codigo": codigo_curso,
                                "nombre": curso.text.strip() if curso.text else codigo_curso
                            })
                            break
        except Exception as e:
            print(f"Error: {e}")

    return jsonify(cursos), 200


@student_bp.route("/api/estudiante/notas", methods=["GET"])
def api_estudiante_notas():
    """API para obtener notas del estudiante"""
    if session.get("rol") != "estudiante":
        return jsonify({"error": "No autorizado"}), 403

    carnet = session.get("carnet")

    try:
        response = requests.get(f"http://localhost:5000/api/notas/estudiante/{carnet}", timeout=5)
        if response.status_code == 200:
            return jsonify(response.json()), 200
        return jsonify([]), 200
    except:
        return jsonify([]), 200


@student_bp.route("/api/estudiante/horarios", methods=["GET"])
def api_estudiante_horarios():
    """API para obtener horarios de tutoría"""
    if session.get("rol") != "estudiante":
        return jsonify({"error": "No autorizado"}), 403

    try:
        response = requests.get("http://localhost:5000/api/horarios/todos", timeout=5)
        if response.status_code == 200:
            return jsonify(response.json()), 200
        return jsonify([]), 200
    except:
        return jsonify([]), 200


@student_bp.route("/api/estudiante/tareas", methods=["GET"])
def api_estudiante_tareas():
    """API para obtener tareas pendientes"""
    if session.get("rol") != "estudiante":
        return jsonify({"error": "No autorizado"}), 403

    return jsonify([]), 200


@student_bp.route("/api/estudiante/anuncios", methods=["GET"])
def api_estudiante_anuncios():
    """API para obtener anuncios"""
    if session.get("rol") != "estudiante":
        return jsonify({"error": "No autorizado"}), 403

    return jsonify([]), 200