from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
import os
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import re

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

# Crear carpetas si no existen
os.makedirs(HORARIOS_FOLDER, exist_ok=True)
os.makedirs(NOTAS_FOLDER, exist_ok=True)

# Diccionario global para almacenar matrices dispersas por tutor
matrices_notas = {}


# ============================================
# FUNCIONES AUXILIARES
# ============================================

def obtener_cursos_tutor(registro_personal):
    """Obtiene los cursos asignados a un tutor desde el XML"""
    cursos = []
    if not os.path.exists(XML_PATH):
        print(f"⚠️ Archivo XML no encontrado: {XML_PATH}")
        return cursos

    try:
        tree = ET.parse(XML_PATH)
        root = tree.getroot()

        # Buscar el tutor
        tutor_encontrado = None
        for tutor in root.findall("tutores/tutor"):
            if tutor.get("registro_personal") == registro_personal:
                tutor_encontrado = tutor
                break

        if tutor_encontrado is None:
            print(f"⚠️ Tutor {registro_personal} no encontrado en XML")
            return cursos

        # Buscar asignaciones en c_tutores
        asignaciones = root.find("asignaciones")
        if asignaciones is not None:
            c_tutores = asignaciones.find("c_tutores")
            if c_tutores is not None:
                for tutor_curso in c_tutores.findall("tutor_curso"):
                    if tutor_curso.text == registro_personal:
                        codigo_curso = tutor_curso.get("codigo")
                        # Buscar nombre del curso
                        cursos_node = root.find("cursos")
                        if cursos_node is not None:
                            for curso in cursos_node.findall("curso"):
                                if curso.get("codigo") == codigo_curso:
                                    cursos.append({
                                        "codigo": codigo_curso,
                                        "nombre": curso.text.strip() if curso.text else ""
                                    })
                                    break

        print(f"📌 Cursos encontrados para tutor {registro_personal}: {[c['codigo'] for c in cursos]}")

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


def obtener_matriz_tutor(registro_personal):
    """Obtiene o crea la matriz dispersa para un tutor"""
    if registro_personal not in matrices_notas:
        matrices_notas[registro_personal] = MatrizDispersa()
        # Intentar cargar desde archivo
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
# RUTAS DEL TUTOR
# ============================================

@tutor_bp.route("/tutor")
def tutor_dashboard():
    """Panel principal del tutor"""
    if session.get("rol") != "tutor":
        return redirect(url_for("auth.login_form"))

    cursos = obtener_cursos_tutor(session.get("registro_personal"))
    return render_template("tutor/dashboard.html",
                           usuario=session.get("usuario"),
                           cursos=cursos)


@tutor_bp.route("/tutor/horarios", methods=["GET", "POST"])
def configurar_horarios():
    """Configurar horarios de tutoría"""
    if session.get("rol") != "tutor":
        return redirect(url_for("auth.login_form"))

    registro_personal = session.get("registro_personal")
    cursos = obtener_cursos_tutor(registro_personal)
    mensaje = None
    errores = []

    print(f"\n🔍 === CONFIGURAR HORARIOS ===")
    print(f"Tutor: {registro_personal}")
    print(f"Cursos del tutor: {[c['codigo'] for c in cursos]}")

    if request.method == "POST":
        if "archivo_horarios" in request.files:
            archivo = request.files["archivo_horarios"]
            if archivo.filename:
                try:
                    contenido = archivo.read().decode("utf-8")
                    lineas = contenido.splitlines()

                    print(f"📄 Archivo recibido: {archivo.filename}")
                    print(f"📝 Total de líneas: {len(lineas)}")

                    horarios_procesados = []

                    for num_linea, linea in enumerate(lineas, 1):
                        linea = linea.strip()

                        # Ignorar líneas vacías o comentarios
                        if not linea or linea.startswith('#'):
                            continue

                        # Buscar curso
                        curso_match = re.search(r'Curso:\s*([^,\s]+)', linea)
                        if not curso_match:
                            errores.append(f"Línea {num_linea}: No se encontró código de curso")
                            continue

                        codigo_curso = curso_match.group(1)

                        # Verificar que el curso pertenezca al tutor
                        cursos_codigos = [c["codigo"] for c in cursos]
                        if codigo_curso not in cursos_codigos:
                            errores.append(f"Línea {num_linea}: Curso {codigo_curso} no asignado al tutor")
                            continue

                        # Buscar HorarioI
                        horario_i_match = re.search(r'HorarioI:\s*(\d{1,2}:\d{2})', linea)
                        if not horario_i_match:
                            errores.append(f"Línea {num_linea}: No se encontró HorarioI válido")
                            continue

                        # Buscar HorarioF
                        horario_f_match = re.search(r'HorarioF:\s*(\d{1,2}:\d{2})', linea)
                        if not horario_f_match:
                            errores.append(f"Línea {num_linea}: No se encontró HorarioF válido")
                            continue

                        # Normalizar horas
                        horario_inicio = horario_i_match.group(1)
                        horario_fin = horario_f_match.group(1)

                        if len(horario_inicio.split(':')[0]) == 1:
                            horario_inicio = '0' + horario_inicio
                        if len(horario_fin.split(':')[0]) == 1:
                            horario_fin = '0' + horario_fin

                        horarios_procesados.append({
                            "curso": codigo_curso,
                            "horario_inicio": horario_inicio,
                            "horario_fin": horario_fin
                        })

                    if horarios_procesados:
                        horarios_actuales = obtener_horarios_tutor(registro_personal)
                        horarios_actuales.extend(horarios_procesados)
                        guardar_horarios_tutor(registro_personal, horarios_actuales)
                        mensaje = f"✅ {len(horarios_procesados)} horarios cargados exitosamente"
                    else:
                        mensaje = "⚠️ No se encontraron horarios válidos en el archivo"

                except Exception as e:
                    print(f"❌ Error: {e}")
                    mensaje = f"❌ Error al procesar archivo: {str(e)}"
            else:
                mensaje = "❌ Por favor, seleccione un archivo"

    horarios = obtener_horarios_tutor(registro_personal)
    return render_template("tutor/horarios.html",
                           usuario=session.get("usuario"),
                           cursos=cursos,
                           horarios=horarios,
                           mensaje=mensaje,
                           errores=errores)


@tutor_bp.route("/tutor/notas", methods=["GET", "POST"])
def ingresar_notas():
    """Ingreso de notas mediante archivo XML"""
    if session.get("rol") != "tutor":
        return redirect(url_for("auth.login_form"))

    registro_personal = session.get("registro_personal")
    cursos = obtener_cursos_tutor(registro_personal)
    mensaje = None

    if request.method == "POST":
        if "archivo_notas" in request.files:
            archivo = request.files["archivo_notas"]
            if archivo.filename and archivo.filename.endswith('.xml'):
                try:
                    tree = ET.parse(archivo)
                    root = tree.getroot()

                    matriz = obtener_matriz_tutor(registro_personal)
                    notas_agregadas = 0
                    notas_rechazadas = 0

                    cursos_codigos = [c["codigo"] for c in cursos]

                    for curso in root.findall("curso"):
                        codigo_curso = curso.get("codigo")

                        if codigo_curso not in cursos_codigos:
                            continue

                        for actividad in curso.findall("actividad"):
                            nombre_actividad = actividad.get("nombre")

                            for nota_elem in actividad.findall("nota"):
                                carnet = nota_elem.get("carnet")
                                try:
                                    nota = float(nota_elem.text)
                                    if matriz.agregar(nombre_actividad, carnet, nota):
                                        notas_agregadas += 1
                                    else:
                                        notas_rechazadas += 1
                                except ValueError:
                                    notas_rechazadas += 1

                    guardar_matriz_tutor(registro_personal)
                    mensaje = f"✅ Notas cargadas: {notas_agregadas} agregadas, {notas_rechazadas} rechazadas"

                except ET.ParseError:
                    mensaje = "❌ Error: El archivo no es un XML válido"
                except Exception as e:
                    mensaje = f"❌ Error al procesar archivo: {str(e)}"
            else:
                mensaje = "❌ Por favor, seleccione un archivo XML válido"

    return render_template("tutor/notas.html",
                           usuario=session.get("usuario"),
                           cursos=cursos,
                           mensaje=mensaje)


@tutor_bp.route("/tutor/reportes", methods=["GET", "POST"])
def reportes():
    """Generar reportes de notas con gráficos"""
    if session.get("rol") != "tutor":
        return redirect(url_for("auth.login_form"))

    registro_personal = session.get("registro_personal")
    cursos = obtener_cursos_tutor(registro_personal)
    matriz = obtener_matriz_tutor(registro_personal)

    actividades = matriz.obtener_todas_actividades()

    promedios = {}
    for actividad in actividades:
        promedios[actividad] = round(matriz.promedio_por_actividad(actividad), 2)

    top_data = {}
    for actividad in actividades:
        top_notas = matriz.top_notas(actividad)
        top_data[actividad] = [
            {"carnet": carnet, "nota": nota}
            for carnet, nota in top_notas[:10]
        ]

    return render_template("tutor/reportes.html",
                           usuario=session.get("usuario"),
                           cursos=cursos,
                           actividades=actividades,
                           promedios=promedios,
                           top_data=json.dumps(top_data))