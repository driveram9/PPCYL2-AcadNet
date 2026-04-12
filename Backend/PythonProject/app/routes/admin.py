from flask import Blueprint, render_template, request
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

admin_bp = Blueprint("admin", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
upload_folder = os.path.join(BASE_DIR, "..", "uploads")
xml_path = os.path.join(upload_folder, "registro.xml")

@admin_bp.route("/")
def admin_dashboard():
    return render_template("admin_dashboard.html")

@admin_bp.route("/upload", methods=["GET", "POST"])
def upload_xml():
    mensaje = None
    contenido_xml = None
    salida = {}

    if request.method == "POST":
        action = request.form.get("action")

        if action == "cargar":
            file = request.files.get("archivo")
            os.makedirs(upload_folder, exist_ok=True)
            file.save(xml_path)
            mensaje = "Archivo cargado correctamente"

        elif action in ["procesar", "guardar"]:
            if action == "guardar":
                nuevo_contenido = request.form.get("xml_editado")
                if nuevo_contenido:
                    with open(xml_path, "w", encoding="utf-8") as f:
                        f.write(nuevo_contenido)

            tree = ET.parse(xml_path)
            root = tree.getroot()
            contenido_xml = ET.tostring(root, encoding="unicode")

            # Recolectar cursos, tutores y estudiantes
            cursos = root.findall("cursos/curso")
            tutores = root.findall("tutores/tutor")
            estudiantes = root.findall("estudiantes/estudiante")

            cursos_codigos = {c.get("codigo") for c in cursos}
            tutores_ids = {t.get("registro_personal") for t in tutores}
            estudiantes_ids = {e.get("carnet") for e in estudiantes}

            # Asignaciones
            tutor_cursos = root.findall("asignaciones/c_tutores/tutor_curso")
            estudiante_cursos = root.findall("asignaciones/c_estudiante/estudiante_curso")

            # Validar tutor_curso
            total_tutor_cursos = len(tutor_cursos)
            correctos_tutor_cursos = sum(
                1 for tc in tutor_cursos
                if tc.get("codigo") in cursos_codigos and tc.text in tutores_ids
            )
            incorrectos_tutor_cursos = total_tutor_cursos - correctos_tutor_cursos

            # Validar estudiante_curso
            total_estudiante_cursos = len(estudiante_cursos)
            correctos_estudiante_cursos = sum(
                1 for ec in estudiante_cursos
                if ec.get("codigo") in cursos_codigos and ec.text in estudiantes_ids
            )
            incorrectos_estudiante_cursos = total_estudiante_cursos - correctos_estudiante_cursos

            # Construir XML de salida
            salida_root = ET.Element("configuraciones_aplicadas")
            ET.SubElement(salida_root, "tutores_cargados").text = str(len(tutores))
            ET.SubElement(salida_root, "estudiantes_cargados").text = str(len(estudiantes))

            asignaciones = ET.SubElement(salida_root, "asignaciones")

            tutores_elem = ET.SubElement(asignaciones, "tutores")
            ET.SubElement(tutores_elem, "total").text = str(total_tutor_cursos)
            ET.SubElement(tutores_elem, "correcto").text = str(correctos_tutor_cursos)
            ET.SubElement(tutores_elem, "incorrecto").text = str(incorrectos_tutor_cursos)

            estudiantes_elem = ET.SubElement(asignaciones, "estudiantes")
            ET.SubElement(estudiantes_elem, "total").text = str(total_estudiante_cursos)
            ET.SubElement(estudiantes_elem, "correcto").text = str(correctos_estudiante_cursos)
            ET.SubElement(estudiantes_elem, "incorrecto").text = str(incorrectos_estudiante_cursos)

            cursos_elem = ET.SubElement(asignaciones, "cursos")
            ET.SubElement(cursos_elem, "total").text = str(len(cursos))
            ET.SubElement(cursos_elem, "correcto").text = str(len(cursos_codigos))
            ET.SubElement(cursos_elem, "incorrecto").text = "0"

            # Pretty-print con minidom para evitar interlineado excesivo
            rough_string = ET.tostring(salida_root, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            salida_xml = reparsed.toprettyxml(indent="    ")

            salida = {"salida_xml": salida_xml}
            mensaje = "Datos procesados correctamente" if action == "procesar" else "Cambios guardados correctamente"

        elif action == "modificar":
            tree = ET.parse(xml_path)
            root = tree.getroot()
            contenido_xml = ET.tostring(root, encoding="unicode")
            mensaje = "Modo edición activado"
            salida["modo_edicion"] = True

        elif action == "limpiar":
            os.remove(xml_path)
            mensaje = "Archivo eliminado"
            contenido_xml = None
            salida = {}

    return render_template(
        "upload.html",
        mensaje=mensaje,
        contenido_xml=contenido_xml,
        salida=salida
    )

@admin_bp.route("/ver_usuarios")
def ver_usuarios():
    estudiantes_data = []

    if os.path.exists(xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()
        estudiantes = root.findall("estudiantes/estudiante")

        for e in estudiantes:
            carnet = e.get("carnet")
            contrasenia = e.get("contrasenia")
            nombre = e.text.strip() if e.text else ""
            estudiantes_data.append({
                "carnet": carnet,
                "contrasenia": contrasenia,
                "nombre": nombre
            })

    return render_template("ver_usuarios.html", estudiantes=estudiantes_data)
