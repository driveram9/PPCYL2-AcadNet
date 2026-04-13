from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
import os
import xml.etree.ElementTree as ET
import json
import re
from io import StringIO

# Importar matriz dispersa
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from matrices.matriz_dispersa import MatrizDispersa

tutor_bp = Blueprint("tutor", __name__)

# ============================================
# CONFIGURACIÓN
# ============================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
HORARIOS_FOLDER = os.path.join(UPLOAD_FOLDER, "horarios")
NOTAS_FOLDER = os.path.join(UPLOAD_FOLDER, "notas")
XML_PATH = os.path.join(UPLOAD_FOLDER, "registro.xml")

# Crear carpetas
os.makedirs(HORARIOS_FOLDER, exist_ok=True)
os.makedirs(NOTAS_FOLDER, exist_ok=True)

# Diccionario global para matrices dispersas
matrices_notas = {}


# ============================================
# FUNCIONES AUXILIARES
# ============================================

def obtener_cursos_tutor(registro_personal):
    """Obtiene los cursos asignados a un tutor desde el XML"""
    cursos = []
    if not os.path.exists(XML_PATH):
        return cursos

    try:
        tree = ET.parse(XML_PATH)
        root = tree.getroot()

        asignaciones = root.find("asignaciones")
        if asignaciones is not None:
            c_tutores = asignaciones.find("c_tutores")
            if c_tutores is not None:
                for tutor_curso in c_tutores.findall("tutor_curso"):
                    if tutor_curso.text == registro_personal:
                        codigo_curso = tutor_curso.get("codigo")
                        cursos_node = root.find("cursos")
                        if cursos_node is not None:
                            for curso in cursos_node.findall("curso"):
                                if curso.get("codigo") == codigo_curso:
                                    cursos.append({
                                        "codigo": codigo_curso,
                                        "nombre": curso.text.strip() if curso.text else ""
                                    })
                                    break
    except Exception as e:
        print(f"Error al cargar cursos: {e}")

    return cursos


def obtener_horarios_tutor(registro_personal):
    """Carga los horarios guardados del tutor"""
    horario_file = os.path.join(HORARIOS_FOLDER, f"{registro_personal}.json")
    if os.path.exists(horario_file):
        try:
            with open(horario_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []


def guardar_horarios_tutor(registro_personal, horarios):
    """Guarda los horarios del tutor"""
    horario_file = os.path.join(HORARIOS_FOLDER, f"{registro_personal}.json")
    with open(horario_file, "w", encoding="utf-8") as f:
        json.dump(horarios, f, indent=2, ensure_ascii=False)


def limpiar_horarios_tutor(registro_personal):
    """Elimina todos los horarios del tutor"""
    horario_file = os.path.join(HORARIOS_FOLDER, f"{registro_personal}.json")
    if os.path.exists(horario_file):
        os.remove(horario_file)
        return True
    return False


def obtener_matriz_tutor(registro_personal):
    """Obtiene o crea la matriz dispersa para un tutor"""
    if registro_personal not in matrices_notas:
        matrices_notas[registro_personal] = MatrizDispersa()
        nota_file = os.path.join(NOTAS_FOLDER, f"{registro_personal}.json")
        if os.path.exists(nota_file):
            try:
                with open(nota_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    matrices_notas[registro_personal].from_dict(data)
            except:
                pass
    return matrices_notas[registro_personal]


def guardar_matriz_tutor(registro_personal):
    """Guarda la matriz dispersa del tutor"""
    matriz = matrices_notas.get(registro_personal)
    if matriz:
        nota_file = os.path.join(NOTAS_FOLDER, f"{registro_personal}.json")
        with open(nota_file, "w", encoding="utf-8") as f:
            json.dump(matriz.to_dict(), f, indent=2, ensure_ascii=False)


# ============================================
# API RUTAS
# ============================================

@tutor_bp.route("/api/cursos/<registro>", methods=["GET"])
def api_get_cursos(registro):
    """Obtener cursos de un tutor"""
    cursos = obtener_cursos_tutor(registro)
    return jsonify(cursos), 200


@tutor_bp.route("/api/horarios/<registro>", methods=["GET"])
def api_get_horarios(registro):
    """Obtener horarios de un tutor"""
    horarios = obtener_horarios_tutor(registro)
    return jsonify(horarios), 200


@tutor_bp.route("/api/horarios/limpiar/<registro>", methods=["DELETE"])
def api_limpiar_horarios(registro):
    """Limpiar todos los horarios de un tutor"""
    try:
        if limpiar_horarios_tutor(registro):
            return jsonify({"success": True, "mensaje": "Horarios eliminados correctamente"}), 200
        else:
            return jsonify({"success": True, "mensaje": "No había horarios para eliminar"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@tutor_bp.route("/api/horarios/cargar/<registro>", methods=["POST"])
def api_cargar_horarios(registro):
    """Cargar horarios desde archivo XML con manejo de codificación"""
    if "archivo_horarios" not in request.files:
        return jsonify({"success": False, "error": "No se envió archivo"}), 400

    archivo = request.files["archivo_horarios"]

    if not archivo.filename.endswith('.xml'):
        return jsonify({"success": False, "error": "El archivo debe ser XML"}), 400

    cursos = obtener_cursos_tutor(registro)
    cursos_codigos = [c["codigo"] for c in cursos]
    horarios_procesados = []

    try:
        # Leer archivo raw
        raw_content = archivo.read()

        # Intentar diferentes codificaciones
        texto = None
        for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
            try:
                texto = raw_content.decode(encoding)
                print(f"✅ Archivo decodificado con {encoding}")
                break
            except UnicodeDecodeError:
                continue

        if texto is None:
            return jsonify({"success": False, "error": "No se pudo decodificar el archivo. Usa UTF-8"}), 400

        # Remover BOM si existe
        if texto.startswith('\ufeff'):
            texto = texto[1:]

        # Parsear XML
        tree = ET.parse(StringIO(texto))
        root = tree.getroot()

        for horario_xml in root.findall("horario"):
            codigo_curso = horario_xml.findtext("curso", "").strip()
            horario_inicio = horario_xml.findtext("horario_inicio", "").strip()
            horario_fin = horario_xml.findtext("horario_fin", "").strip()

            if not codigo_curso or not horario_inicio or not horario_fin:
                continue

            if codigo_curso not in cursos_codigos:
                continue

            if not re.match(r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$', horario_inicio):
                continue

            if not re.match(r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$', horario_fin):
                continue

            horarios_procesados.append({
                "curso": codigo_curso,
                "horario_inicio": horario_inicio,
                "horario_fin": horario_fin
            })

        if horarios_procesados:
            guardar_horarios_tutor(registro, horarios_procesados)
            return jsonify({
                "success": True,
                "mensaje": f"✅ {len(horarios_procesados)} horarios cargados correctamente"
            })
        else:
            return jsonify({
                "success": False,
                "error": "No se encontraron horarios válidos en el archivo"
            }), 400

    except ET.ParseError as e:
        return jsonify({"success": False, "error": f"Error en el XML: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@tutor_bp.route("/api/notas/<registro>", methods=["POST"])
def api_cargar_notas(registro):
    """Cargar notas desde archivo XML con manejo de codificación"""
    if "archivo_notas" not in request.files:
        return jsonify({"success": False, "error": "No se envió archivo"}), 400

    archivo = request.files["archivo_notas"]

    if not archivo.filename.endswith('.xml'):
        return jsonify({"success": False, "error": "El archivo debe ser XML"}), 400

    cursos = obtener_cursos_tutor(registro)
    cursos_codigos = [c["codigo"] for c in cursos]
    matriz = obtener_matriz_tutor(registro)

    notas_agregadas = 0
    notas_rechazadas = 0

    try:
        # Leer archivo raw
        raw_content = archivo.read()

        # Intentar diferentes codificaciones
        texto = None
        for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
            try:
                texto = raw_content.decode(encoding)
                print(f"✅ Notas decodificado con {encoding}")
                break
            except UnicodeDecodeError:
                continue

        if texto is None:
            return jsonify({"success": False, "error": "No se pudo decodificar el archivo. Usa UTF-8"}), 400

        # Remover BOM si existe
        if texto.startswith('\ufeff'):
            texto = texto[1:]

        # Parsear XML
        tree = ET.parse(StringIO(texto))
        root = tree.getroot()

        for curso in root.findall("curso"):
            codigo_curso = curso