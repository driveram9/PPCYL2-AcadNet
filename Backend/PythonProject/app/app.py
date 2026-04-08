import os
import xml.etree.ElementTree as ET
from flask import Flask, request, render_template, url_for, redirect, session
from werkzeug.utils import secure_filename

def generar_salida(contenido):
    root = ET.fromstring(contenido)

    cursos_node = root.find("cursos")
    tutores_node = root.find("tutores")
    estudiantes_node = root.find("estudiantes")

    num_cursos = len(cursos_node) if cursos_node is not None else 0
    num_tutores = len(tutores_node) if tutores_node is not None else 0
    num_estudiantes = len(estudiantes_node) if estudiantes_node is not None else 0

    cursos = {c.get("codigo") for c in cursos_node} if cursos_node is not None else set()
    tutores = {t.get("registro_personal") for t in tutores_node} if tutores_node is not None else set()
    estudiantes = {e.get("carnet") for e in estudiantes_node} if estudiantes_node is not None else set()

    total_tutores_asig = correctos_tutores = incorrectos_tutores = 0
    asign_tutores = root.find("asignaciones/c_tutores")
    if asign_tutores is not None:
        for tc in asign_tutores.findall("tutor_curso"):
            total_tutores_asig += 1
            if tc.get("codigo") in cursos and tc.text in tutores:
                correctos_tutores += 1
            else:
                incorrectos_tutores += 1

    total_estudiantes_asig = correctos_estudiantes = incorrectos_estudiantes = 0
    asign_estudiantes = root.find("asignaciones/c_estudiante")
    if asign_estudiantes is not None:
        for ec in asign_estudiantes.findall("estudiante_curso"):
            total_estudiantes_asig += 1
            if ec.get("codigo") in cursos and ec.text in estudiantes:
                correctos_estudiantes += 1
            else:
                incorrectos_estudiantes += 1

    salida = f"""<?xml version="1.0"?>
<configuraciones_aplicadas>
    <cursos_cargados>{num_cursos}</cursos_cargados>
    <tutores_cargados>{num_tutores}</tutores_cargados>
    <estudiantes_cargados>{num_estudiantes}</estudiantes_cargados>
    <asignaciones>
        <tutores>
            <total>{total_tutores_asig}</total>
            <correcto>{correctos_tutores}</correcto>
            <incorrecto>{incorrectos_tutores}</incorrecto>
        </tutores>
        <estudiantes>
            <total>{total_estudiantes_asig}</total>
            <correcto>{correctos_estudiantes}</correcto>
            <incorrecto>{incorrectos_estudiantes}</incorrecto>
        </estudiantes>
    </asignaciones>
</configuraciones_aplicadas>"""
    return salida

def cargar_usuarios():
    usuarios = []
    ruta_xml = os.path.join(os.path.dirname(__file__), "Base.xml")
    if not os.path.exists(ruta_xml):
        return usuarios
    try:
        tree = ET.parse(ruta_xml)
        root = tree.getroot()
        for usuario in root.findall(".//usuario"):
            datos = {
                "id": usuario.get("id", "0"),
                "nombre": usuario.findtext("nombre", "Sin nombre"),
                "rol": usuario.findtext("rol", "sin_rol"),
                "login": usuario.findtext("login", ""),
                "contrasenia": usuario.findtext("contrasenia", ""),
                "email": usuario.findtext("email", "no@email.com"),
                "estado": usuario.findtext("estado", "activo")
            }
            usuarios.append(datos)
    except ET.ParseError:
        pass
    except Exception:
        pass
    return usuarios

def validar_login(usuario, contrasenia):
    usuarios = cargar_usuarios()
    for user in usuarios:
        if user["login"] == usuario and user["contrasenia"] == contrasenia:
            if user["estado"] == "activo":
                return user
            else:
                return {"error": "usuario_inactivo"}
    return None

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "clave_para_flask"

@app.route("/")
def index():
    session.clear()
    if session.get("usuario_rol"):
        rol = session.get("usuario_rol")
        if rol == "administrador":
            return redirect(url_for("admin_dashboard"))
        elif rol == "tutor":
            return redirect(url_for("tutor_dashboard"))
        elif rol == "estudiante":
            return redirect(url_for("estudiante_dashboard"))
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    usuario = request.form.get('usuario','')
    contrasenia = request.form.get('contrasenia','')
    if not usuario or not contrasenia:
        return render_template("index.html", error="Por favor, complete todos los campos")
    resultado = validar_login(usuario, contrasenia)
    if resultado is None:
        return render_template("index.html", error="Usuario o contraseña incorrectos")
    if isinstance(resultado, dict) and resultado.get("error") == "usuario_inactivo":
        return render_template("index.html", error="Su cuenta está inactiva. Contacte al administrador.")
    session["usuario_id"] = resultado["id"]
    session["usuario_nombre"] = resultado["nombre"]
    session["usuario_rol"] = resultado["rol"]
    session["usuario_login"] = resultado["login"]
    session["usuario_email"] = resultado["email"]
    rol = resultado["rol"]
    if rol == "administrador":
        return redirect(url_for("admin_dashboard"))
    elif rol == "tutor":
        return redirect(url_for("tutor_dashboard"))
    elif rol == "estudiante":
        return redirect(url_for("estudiante_dashboard"))
    else:
        return render_template("index.html", error=f"Rol '{rol}' no reconocido")

@app.route("/admin", methods=["GET", "POST"])
def admin_dashboard():
    contenido_xml = request.form.get("xml_texto", "")
    salida_xml = ""
    if request.method == "POST":
        accion = request.form.get("accion")
        if accion == "cargar":
            archivo = request.files.get("archivo")
            if archivo and archivo.filename.endswith(".xml"):
                filename = secure_filename("archivo")
                ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                archivo.save(ruta)
                with open(ruta, "r", encoding="utf-8") as f:
                    contenido_xml = f.read()
                session["archivo_xml"] = ruta
                session["contenido_xml"] = contenido_xml
        elif accion == "procesar":
            ruta = session.get("archivo_xml")
            if ruta and os.path.exists(ruta):
                with open(ruta, "r", encoding="utf-8") as f:
                    contenido_xml = f.read()
                salida_xml = generar_salida(contenido_xml)
        elif accion == "limpiar":
            contenido_xml = ""
            salida_xml = ""
            session.pop("archivo_xml", None)
            session.pop("contenido_xml", None)
    return render_template("admin.html", xml=contenido_xml, salida=salida_xml)

@app.route("/admin/procesar", methods=["POST"])
def admin_procesar():
    contenido = session.get("contenido_xml", "")
    salida_xml = generar_salida(contenido)
    return render_template("admin.html", xml=contenido, salida=salida_xml)

@app.route("/tutor")
def tutor_dashboard():
    return render_template("tutor.html")

if __name__ == '__main__':
    app.run(debug=True, port=5000)

def procesar_xml(contenido):
    root = ET.fromstring(contenido)
    cursos = []
    for curso in root.find("cursos"):
        cursos.append({"codigo": curso.get("codigo"), "nombre": curso.text})
    tutores = []
    for tutor in root.find("tutores"):
        tutores.append({
            "registro": tutor.get("registro_personal"),
            "nombre": tutor.text,
            "contrasenia": tutor.get("contrasenia")
        })
    estudiantes = []
    for est in root.find("estudiantes"):
        estudiantes.append({
            "carnet": est.get("carnet"),
            "nombre": est.text,
            "contrasenia": est.get("contrasenia")
        })
    return cursos, tutores, estudiantes
