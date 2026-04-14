from flask import Blueprint, render_template, request, jsonify
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

admin_bp = Blueprint("admin", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
upload_folder = os.path.join(BASE_DIR, "..", "uploads")
xml_path = os.path.join(upload_folder, "registro.xml")


@admin_bp.route("/api/admin/cursos", methods=["GET"])
def api_get_cursos():
    """Obtener lista de cursos"""
    cursos = []
    if os.path.exists(xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for curso in root.findall("cursos/curso"):
            cursos.append({
                "codigo": curso.get("codigo"),
                "nombre": curso.text.strip() if curso.text else ""
            })
    return jsonify(cursos)


@admin_bp.route("/api/admin/tutores", methods=["GET"])
def api_get_tutores():
    """Obtener lista de tutores con sus cursos"""
    tutores = []
    if os.path.exists(xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Obtener asignaciones tutor-curso
        asignaciones = {}
        for tc in root.findall("asignaciones/c_tutores/tutor_curso"):
            codigo = tc.get("codigo")
            tutor_id = tc.text
            if tutor_id not in asignaciones:
                asignaciones[tutor_id] = []
            asignaciones[tutor_id].append(codigo)

        for tutor in root.findall("tutores/tutor"):
            registro = tutor.get("registro_personal")
            tutores.append({
                "registro": registro,
                "nombre": tutor.text.strip() if tutor.text else "",
                "contrasenia": tutor.get("contrasenia"),
                "cursos": asignaciones.get(registro, [])
            })
    return jsonify(tutores)


@admin_bp.route("/api/admin/estudiantes", methods=["GET"])
def api_get_estudiantes():
    """Obtener lista de estudiantes con sus cursos"""
    estudiantes = []
    if os.path.exists(xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Obtener asignaciones estudiante-curso
        asignaciones = {}
        for ec in root.findall("asignaciones/c_estudiante/estudiante_curso"):
            codigo = ec.get("codigo")
            carnet = ec.text
            if carnet not in asignaciones:
                asignaciones[carnet] = []
            asignaciones[carnet].append(codigo)

        for estudiante in root.findall("estudiantes/estudiante"):
            carnet = estudiante.get("carnet")
            estudiantes.append({
                "carnet": carnet,
                "nombre": estudiante.text.strip() if estudiante.text else "",
                "contrasenia": estudiante.get("contrasenia"),
                "cursos": asignaciones.get(carnet, [])
            })
    return jsonify(estudiantes)


@admin_bp.route("/api/admin/upload", methods=["POST"])
def api_upload_xml():
    """Cargar archivo XML"""
    if "archivo" not in request.files:
        return jsonify({"success": False, "error": "No se envió archivo"}), 400

    file = request.files["archivo"]
    if not file.filename.endswith('.xml'):
        return jsonify({"success": False, "error": "El archivo debe ser XML"}), 400

    os.makedirs(upload_folder, exist_ok=True)
    file.save(xml_path)

    return jsonify({"success": True, "mensaje": "Archivo cargado correctamente"})


@admin_bp.route("/api/admin/procesar", methods=["GET"])
def api_procesar_xml():
    """Procesar XML y obtener estadísticas"""
    if not os.path.exists(xml_path):
        return jsonify({"success": False, "error": "No hay archivo cargado"}), 404

    tree = ET.parse(xml_path)
    root = tree.getroot()

    cursos = root.findall("cursos/curso")
    tutores = root.findall("tutores/tutor")
    estudiantes = root.findall("estudiantes/estudiante")

    cursos_codigos = {c.get("codigo") for c in cursos}
    tutores_ids = {t.get("registro_personal") for t in tutores}
    estudiantes_ids = {e.get("carnet") for e in estudiantes}

    # Asignaciones
    tutor_cursos = root.findall("asignaciones/c_tutores/tutor_curso")
    estudiante_cursos = root.findall("asignaciones/c_estudiante/estudiante_curso")

    total_tutor_cursos = len(tutor_cursos)
    correctos_tutor_cursos = sum(
        1 for tc in tutor_cursos
        if tc.get("codigo") in cursos_codigos and tc.text in tutores_ids
    )

    total_estudiante_cursos = len(estudiante_cursos)
    correctos_estudiante_cursos = sum(
        1 for ec in estudiante_cursos
        if ec.get("codigo") in cursos_codigos and ec.text in estudiantes_ids
    )

    return jsonify({
        "success": True,
        "cursos": {
            "total": len(cursos),
            "lista": [{"codigo": c.get("codigo"), "nombre": c.text} for c in cursos]
        },
        "tutores": {
            "total": len(tutores),
            "correctos": correctos_tutor_cursos,
            "incorrectos": total_tutor_cursos - correctos_tutor_cursos,
            "total_asignaciones": total_tutor_cursos
        },
        "estudiantes": {
            "total": len(estudiantes),
            "correctos": correctos_estudiante_cursos,
            "incorrectos": total_estudiante_cursos - correctos_estudiante_cursos,
            "total_asignaciones": total_estudiante_cursos
        }
    })


@admin_bp.route("/api/admin/xml", methods=["GET"])
def api_get_xml():
    """Obtener contenido del XML para editar"""
    if not os.path.exists(xml_path):
        return jsonify({"success": False, "error": "No hay archivo cargado"}), 404

    with open(xml_path, "r", encoding="utf-8") as f:
        contenido = f.read()

    return jsonify({"success": True, "contenido": contenido})


@admin_bp.route("/api/admin/xml", methods=["PUT"])
def api_update_xml():
    """Guardar contenido XML editado"""
    data = request.get_json()
    nuevo_contenido = data.get("contenido", "")

    if not nuevo_contenido:
        return jsonify({"success": False, "error": "Contenido vacío"}), 400

    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(nuevo_contenido)

    return jsonify({"success": True, "mensaje": "XML guardado correctamente"})


@admin_bp.route("/api/admin/limpiar", methods=["DELETE"])
def api_limpiar_xml():
    """Eliminar archivo XML"""
    if os.path.exists(xml_path):
        os.remove(xml_path)
        return jsonify({"success": True, "mensaje": "Archivo eliminado"})
    return jsonify({"success": False, "error": "No hay archivo para eliminar"}), 404