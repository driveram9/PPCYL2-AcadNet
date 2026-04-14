from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
import os
import xml.etree.ElementTree as ET
import json
import re
from io import StringIO
import datetime

# Importar matriz dispersa
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from matrices.matriz_dispersa import MatrizDispersa

tutor_bp = Blueprint("tutor", __name__)

# ============================================
# CONFIGURACIÓN (CORREGIDA)
# ============================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
HORARIOS_FOLDER = os.path.join(UPLOAD_FOLDER, "horarios")
NOTAS_FOLDER = os.path.join(UPLOAD_FOLDER, "notas")

# ✅ XML en la raíz de app (no dentro de uploads)
XML_PATH = os.path.join(BASE_DIR, "registro.xml")

# Crear carpetas
os.makedirs(HORARIOS_FOLDER, exist_ok=True)
os.makedirs(NOTAS_FOLDER, exist_ok=True)

# Debug - mostrar ruta del XML al iniciar
print(f"📁 XML_PATH: {XML_PATH}")
print(f"📁 ¿Existe XML? {os.path.exists(XML_PATH)}")

# Diccionario global para matrices dispersas
matrices_notas = {}


# ============================================
# FUNCIONES AUXILIARES
# ============================================

def obtener_cursos_tutor(registro_personal):
    """Obtiene los cursos asignados a un tutor desde el XML"""
    cursos = []
    if not os.path.exists(XML_PATH):
        print(f"❌ XML no encontrado en: {XML_PATH}")
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


def obtener_info_tutor(registro_personal):
    """Obtener información de un tutor por su registro"""
    if not os.path.exists(XML_PATH):
        return {"nombre": "Desconocido", "registro": registro_personal}

    try:
        tree = ET.parse(XML_PATH)
        root = tree.getroot()

        for tutor in root.findall("tutores/tutor"):
            if tutor.get("registro_personal") == registro_personal:
                return {
                    "nombre": tutor.text.strip() if tutor.text else "Desconocido",
                    "registro": registro_personal
                }
    except:
        pass

    return {"nombre": "Desconocido", "registro": registro_personal}


def estudiante_en_curso(carnet, codigo_curso):
    """Verifica si un estudiante está inscrito en un curso"""
    if not os.path.exists(XML_PATH):
        return False

    try:
        tree = ET.parse(XML_PATH)
        root = tree.getroot()

        for ec in root.findall("asignaciones/c_estudiante/estudiante_curso"):
            if ec.get("codigo") == codigo_curso and ec.text == carnet:
                return True
    except:
        pass

    return False


def obtener_fecha_nota(registro_tutor, actividad, carnet):
    """Obtener la fecha de cuando se registró la nota"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


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
    print("=" * 50)
    print("🔍 INICIANDO CARGA DE HORARIOS")
    print(f"Registro: {registro}")

    if "archivo_horarios" not in request.files:
        print("❌ No se encontró el archivo en la petición")
        return jsonify({"success": False, "error": "No se envió archivo"}), 400

    archivo = request.files["archivo_horarios"]
    print(f"📄 Nombre del archivo: {archivo.filename}")

    if not archivo.filename.endswith('.xml'):
        print("❌ El archivo no es XML")
        return jsonify({"success": False, "error": "El archivo debe ser XML"}), 400

    cursos = obtener_cursos_tutor(registro)
    cursos_codigos = [c["codigo"] for c in cursos]
    print(f"📌 Cursos del tutor: {cursos_codigos}")

    horarios_procesados = []

    try:
        raw_content = archivo.read()
        print(f"📦 Tamaño del archivo: {len(raw_content)} bytes")

        texto = None
        for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
            try:
                texto = raw_content.decode(encoding)
                print(f"✅ Archivo decodificado con {encoding}")
                break
            except UnicodeDecodeError:
                print(f"❌ Falló decodificación con {encoding}")
                continue

        if texto is None:
            print("❌ No se pudo decodificar el archivo")
            return jsonify({"success": False, "error": "No se pudo decodificar el archivo. Usa UTF-8"}), 400

        if texto.startswith('\ufeff'):
            texto = texto[1:]
            print("✅ BOM removido")

        print(f"📝 Contenido del archivo (primeros 200 chars): {texto[:200]}")

        tree = ET.parse(StringIO(texto))
        root = tree.getroot()
        print(f"✅ XML parseado correctamente")
        print(f"📌 Elementos horario encontrados: {len(root.findall('horario'))}")

        for horario_xml in root.findall("horario"):
            codigo_curso = horario_xml.findtext("curso", "").strip()
            horario_inicio = horario_xml.findtext("horario_inicio", "").strip()
            horario_fin = horario_xml.findtext("horario_fin", "").strip()

            print(f"   - Curso: {codigo_curso}, Inicio: {horario_inicio}, Fin: {horario_fin}")

            if not codigo_curso or not horario_inicio or not horario_fin:
                print(f"      ❌ Campos vacíos, ignorado")
                continue

            if codigo_curso not in cursos_codigos:
                print(f"      ❌ Curso no asignado al tutor")
                continue

            if not re.match(r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$', horario_inicio):
                print(f"      ❌ Horario inicio inválido: {horario_inicio}")
                continue

            if not re.match(r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$', horario_fin):
                print(f"      ❌ Horario fin inválido: {horario_fin}")
                continue

            horarios_procesados.append({
                "curso": codigo_curso,
                "horario_inicio": horario_inicio,
                "horario_fin": horario_fin
            })
            print(f"      ✅ Horario válido agregado")

        if horarios_procesados:
            guardar_horarios_tutor(registro, horarios_procesados)
            print(f"✅ {len(horarios_procesados)} horarios guardados")
            return jsonify({
                "success": True,
                "mensaje": f"✅ {len(horarios_procesados)} horarios cargados correctamente"
            })
        else:
            print("❌ No se encontraron horarios válidos")
            return jsonify({
                "success": False,
                "error": "No se encontraron horarios válidos en el archivo. Verifica el formato."
            }), 400

    except ET.ParseError as e:
        print(f"❌ Error de parseo XML: {e}")
        return jsonify({"success": False, "error": f"Error en el XML: {str(e)}"}), 400
    except Exception as e:
        print(f"❌ Error general: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@tutor_bp.route("/api/notas/<registro>", methods=["POST"])
def api_cargar_notas(registro):
    """Cargar notas desde archivo XML con manejo de codificación"""
    print("=" * 50)
    print("🔍 INICIANDO CARGA DE NOTAS")
    print(f"Registro: {registro}")

    if "archivo_notas" not in request.files:
        print("❌ No se encontró el archivo en la petición")
        return jsonify({"success": False, "error": "No se envió archivo"}), 400

    archivo = request.files["archivo_notas"]
    print(f"📄 Nombre del archivo: {archivo.filename}")

    if not archivo.filename.endswith('.xml'):
        print("❌ El archivo no es XML")
        return jsonify({"success": False, "error": "El archivo debe ser XML"}), 400

    cursos = obtener_cursos_tutor(registro)
    cursos_codigos = [c["codigo"] for c in cursos]
    print(f"📌 Cursos del tutor: {cursos_codigos}")
    matriz = obtener_matriz_tutor(registro)

    notas_agregadas = 0
    notas_rechazadas = 0

    try:
        raw_content = archivo.read()
        print(f"📦 Tamaño del archivo: {len(raw_content)} bytes")

        texto = None
        for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
            try:
                texto = raw_content.decode(encoding)
                print(f"✅ Archivo decodificado con {encoding}")
                break
            except UnicodeDecodeError:
                print(f"❌ Falló decodificación con {encoding}")
                continue

        if texto is None:
            print("❌ No se pudo decodificar el archivo")
            return jsonify({"success": False, "error": "No se pudo decodificar el archivo. Usa UTF-8"}), 400

        if texto.startswith('\ufeff'):
            texto = texto[1:]
            print("✅ BOM removido")

        tree = ET.parse(StringIO(texto))
        root = tree.getroot()
        print(f"✅ XML parseado correctamente")

        for curso in root.findall("curso"):
            codigo_curso = curso.get("codigo")
            print(f"📌 Procesando curso: {codigo_curso}")

            if codigo_curso not in cursos_codigos:
                print(f"   ❌ Curso no asignado al tutor")
                continue

            for actividad in curso.findall("actividad"):
                nombre_actividad = actividad.get("nombre")
                print(f"   📌 Actividad: {nombre_actividad}")

                for nota_elem in actividad.findall("nota"):
                    carnet = nota_elem.get("carnet")
                    try:
                        nota = float(nota_elem.text)
                        if matriz.agregar(nombre_actividad, carnet, nota):
                            notas_agregadas += 1
                            print(f"      ✅ Nota {nota} agregada para {carnet}")
                        else:
                            notas_rechazadas += 1
                            print(f"      ❌ Nota {nota} rechazada (fuera de rango 0-100)")
                    except ValueError:
                        notas_rechazadas += 1
                        print(f"      ❌ Nota inválida para {carnet}: {nota_elem.text}")

        guardar_matriz_tutor(registro)
        print(f"✅ Notas cargadas: {notas_agregadas} agregadas, {notas_rechazadas} rechazadas")
        return jsonify({
            "success": True,
            "mensaje": f"{notas_agregadas} notas agregadas, {notas_rechazadas} rechazadas"
        })

    except ET.ParseError as e:
        print(f"❌ Error de parseo XML: {e}")
        return jsonify({"success": False, "error": f"Error en el XML: {str(e)}"}), 400
    except Exception as e:
        print(f"❌ Error general: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@tutor_bp.route("/api/reportes/<registro>", methods=["GET"])
def api_get_reportes(registro):
    """Obtener datos para reportes"""
    matriz = obtener_matriz_tutor(registro)
    actividades = matriz.obtener_todas_actividades()

    promedios = {}
    for actividad in actividades:
        promedios[actividad] = round(matriz.promedio_por_actividad(actividad), 2)

    top_data = {}
    for actividad in actividades:
        top_notas = matriz.top_notas(actividad)
        top_data[actividad] = [{"carnet": c, "nota": n} for c, n in top_notas[:10]]

    return jsonify({
        "actividades": actividades,
        "promedios": promedios,
        "top_data": top_data
    }), 200


# ============================================
# RUTAS PARA ESTUDIANTES (CONSULTAR NOTAS Y HORARIOS)
# ============================================

@tutor_bp.route("/api/notas/estudiante/<carnet>", methods=["GET"])
def api_get_notas_estudiante(carnet):
    """Obtener todas las notas de un estudiante específico"""
    print("=" * 50)
    print("🔍 BUSCANDO NOTAS PARA ESTUDIANTE")
    print(f"Carnet: {carnet}")

    todas_notas = []

    for registro_personal, matriz in matrices_notas.items():
        notas_estudiante = matriz.obtener_por_estudiante(carnet)

        if notas_estudiante:
            print(f"📌 Notas encontradas en tutor: {registro_personal}")
            tutor_info = obtener_info_tutor(registro_personal)
            cursos_tutor = obtener_cursos_tutor(registro_personal)

            for actividad, nota in notas_estudiante.items():
                curso_asignado = None
                for curso in cursos_tutor:
                    if estudiante_en_curso(carnet, curso["codigo"]):
                        curso_asignado = curso
                        break

                todas_notas.append({
                    "tutor": tutor_info["nombre"],
                    "tutor_registro": registro_personal,
                    "curso": curso_asignado["codigo"] if curso_asignado else "Desconocido",
                    "curso_nombre": curso_asignado["nombre"] if curso_asignado else "Desconocido",
                    "actividad": actividad,
                    "nota": nota,
                    "fecha": obtener_fecha_nota(registro_personal, actividad, carnet)
                })

    todas_notas.sort(key=lambda x: x.get("fecha", ""), reverse=True)
    print(f"✅ Total notas encontradas: {len(todas_notas)}")
    return jsonify(todas_notas), 200


@tutor_bp.route("/api/horarios/todos", methods=["GET"])
def api_get_todos_horarios():
    """Obtener todos los horarios de tutoría (para estudiantes)"""
    todos_horarios = []

    if os.path.exists(HORARIOS_FOLDER):
        for archivo in os.listdir(HORARIOS_FOLDER):
            if archivo.endswith('.json'):
                registro_tutor = archivo.replace('.json', '')
                try:
                    with open(os.path.join(HORARIOS_FOLDER, archivo), "r", encoding="utf-8") as f:
                        horarios = json.load(f)
                        tutor_info = obtener_info_tutor(registro_tutor)
                        for h in horarios:
                            todos_horarios.append({
                                "curso": h.get("curso"),
                                "horario_inicio": h.get("horario_inicio"),
                                "horario_fin": h.get("horario_fin"),
                                "tutor": tutor_info["nombre"],
                                "tutor_registro": registro_tutor
                            })
                except:
                    pass

    return jsonify(todos_horarios), 200


@tutor_bp.route("/api/estudiante/cursos/<carnet>", methods=["GET"])
def api_get_cursos_estudiante(carnet):
    """Obtener cursos en los que está inscrito un estudiante"""
    cursos = []

    if os.path.exists(XML_PATH):
        try:
            tree = ET.parse(XML_PATH)
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
            print(f"Error al obtener cursos del estudiante: {e}")

    return jsonify(cursos), 200


@tutor_bp.route("/api/estudiante/tareas/<carnet>", methods=["GET"])
def api_get_tareas_estudiante(carnet):
    """Obtener tareas pendientes del estudiante (placeholder)"""
    return jsonify([]), 200


@tutor_bp.route("/api/anuncios", methods=["GET"])
def api_get_anuncios():
    """Obtener anuncios generales (placeholder)"""
    return jsonify([]), 200