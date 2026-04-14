from flask import Blueprint, render_template, request, jsonify
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
import traceback  # Añade al inicio del archivo
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
    """Procesar XML y devolver el XML de salida"""
    if not os.path.exists(xml_path):
        return jsonify({"success": False, "error": "No hay archivo cargado"}), 404

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        salida_xml = generar_xml_salida(root)
        return jsonify({"success": True, "salida_xml": salida_xml})
    except ET.ParseError as e:
        return jsonify({"success": False, "error": f"Error de sintaxis en XML: {str(e)}"}), 400
    except Exception as e:
        print("❌ Error al procesar XML:")
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Error interno: {str(e)}"}), 500

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


# ============================================
# NUEVA FUNCIÓN: GENERAR XML DE SALIDA
# ============================================


def generar_xml_salida(root_entrada):
    """Genera el XML de salida según el formato especificado (más tolerante)"""
    # Buscar las secciones (con nombres exactos)
    cursos = root_entrada.findall("cursos/curso")
    tutores = root_entrada.findall("tutores/tutor")
    estudiantes = root_entrada.findall("estudiantes/estudiante")

    # Si no encuentra, probar con mayúsculas (por si acaso)
    if not cursos:
        cursos = root_entrada.findall("Cursos/Curso")
    if not tutores:
        tutores = root_entrada.findall("Tutores/Tutor")
    if not estudiantes:
        estudiantes = root_entrada.findall("Estudiantes/Estudiante")

    cursos_codigos = {c.get("codigo") for c in cursos if c.get("codigo")}
    tutores_ids = {t.get("registro_personal") for t in tutores if t.get("registro_personal")}
    estudiantes_ids = {e.get("carnet") for e in estudiantes if e.get("carnet")}

    # Asignaciones
    tutor_cursos = root_entrada.findall("asignaciones/c_tutores/tutor_curso")
    estudiante_cursos = root_entrada.findall("asignaciones/c_estudiante/estudiante_curso")

    total_tutor_cursos = len(tutor_cursos)
    correctos_tutor_cursos = 0
    for tc in tutor_cursos:
        codigo = tc.get("codigo")
        tutor_id = tc.text
        if codigo in cursos_codigos and tutor_id in tutores_ids:
            correctos_tutor_cursos += 1

    total_estudiante_cursos = len(estudiante_cursos)
    correctos_estudiante_cursos = 0
    for ec in estudiante_cursos:
        codigo = ec.get("codigo")
        estudiante_id = ec.text
        if codigo in cursos_codigos and estudiante_id in estudiantes_ids:
            correctos_estudiante_cursos += 1

    # Construir XML de salida
    salida_root = ET.Element("configuraciones_aplicadas")
    ET.SubElement(salida_root, "tutores_cargados").text = str(len(tutores))
    ET.SubElement(salida_root, "estudiantes_cargados").text = str(len(estudiantes))

    asignaciones = ET.SubElement(salida_root, "asignaciones")

    tutores_elem = ET.SubElement(asignaciones, "tutores")
    ET.SubElement(tutores_elem, "total").text = str(total_tutor_cursos)
    ET.SubElement(tutores_elem, "correcto").text = str(correctos_tutor_cursos)
    ET.SubElement(tutores_elem, "incorrecto").text = str(total_tutor_cursos - correctos_tutor_cursos)

    estudiantes_elem = ET.SubElement(asignaciones, "estudiantes")
    ET.SubElement(estudiantes_elem, "total").text = str(total_estudiante_cursos)
    ET.SubElement(estudiantes_elem, "correcto").text = str(correctos_estudiante_cursos)
    ET.SubElement(estudiantes_elem, "incorrecto").text = str(total_estudiante_cursos - correctos_estudiante_cursos)

    # Pretty-print
    rough_string = ET.tostring(salida_root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ")

