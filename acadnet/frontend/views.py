from django.shortcuts import render, redirect
import xml.etree.ElementTree as ET
import os

# Ruta del XML (MISMA carpeta que views.py)
RUTA_XML = os.path.join(os.path.dirname(__file__), 'registro.xml')


def cargar_datos():
    print("Ruta XML:", RUTA_XML)
    print("¿Existe?:", os.path.exists(RUTA_XML))

    if not os.path.exists(RUTA_XML):
        return None

    tree = ET.parse(RUTA_XML)
    root = tree.getroot()

    datos = {
        "estudiantes": {},
        "tutores": {},
        "cursos": {},
        "asignaciones_tutor": {},
        "asignaciones_estudiante": {}
    }

    # CURSOS
    for curso in root.findall(".//curso"):
        datos["cursos"][curso.get("codigo")] = curso.text

    # TUTORES
    for tut in root.findall(".//tutor"):
        datos["tutores"][tut.get("registro_personal")] = {
            "nombre": tut.text,
            "contrasenia": tut.get("contrasenia")
        }

    # ESTUDIANTES
    for est in root.findall(".//estudiante"):
        datos["estudiantes"][est.get("carnet")] = {
            "nombre": est.text,
            "contrasenia": est.get("contrasenia")
        }

    # ASIGNACIONES
    for t in root.findall(".//tutor_curso"):
        datos["asignaciones_tutor"].setdefault(t.text, []).append(t.get("codigo"))

    for e in root.findall(".//estudiante_curso"):
        datos["asignaciones_estudiante"].setdefault(e.text, []).append(e.get("codigo"))

    return datos


def login_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasenia = request.POST.get('contrasenia')

        datos = cargar_datos()

        # ADMIN
        if usuario == "AdminPPCYL2" and contrasenia == "AdminPPCYL2771":
            request.session['rol'] = 'admin'
            request.session['nombre'] = 'Administrador'
            return redirect('admin')

        # ESTUDIANTE
        if usuario in datos["estudiantes"]:
            if contrasenia == datos["estudiantes"][usuario]["contrasenia"]:
                request.session['rol'] = 'estudiante'
                request.session['nombre'] = datos["estudiantes"][usuario]["nombre"]
                request.session['carnet'] = usuario
                return redirect('student')

        # TUTOR
        if usuario in datos["tutores"]:
            if contrasenia == datos["tutores"][usuario]["contrasenia"]:
                request.session['rol'] = 'tutor'
                request.session['nombre'] = datos["tutores"][usuario]["nombre"]
                request.session['registro'] = usuario
                return redirect('tutor')

        return render(request, 'login.html', {'error': 'Datos incorrectos'})

    return render(request, 'login.html')


def dashboard_student(request):
    if request.session.get('rol') != 'estudiante':
        return redirect('login')

    datos = cargar_datos()
    carnet = request.session.get('carnet')

    cursos_codigos = datos["asignaciones_estudiante"].get(carnet, [])
    cursos = [datos["cursos"][c] for c in cursos_codigos]

    return render(request, 'dashboardStudent.html', {
        'nombre': request.session.get('nombre'),
        'cursos': cursos
    })


def dashboard_tutor(request):
    if request.session.get('rol') != 'tutor':
        return redirect('login')

    datos = cargar_datos()
    registro = request.session.get('registro')

    cursos_codigos = datos["asignaciones_tutor"].get(registro, [])
    cursos = [datos["cursos"][c] for c in cursos_codigos]

    return render(request, 'dashboardTutor.html', {
        'nombre': request.session.get('nombre'),
        'cursos': cursos
    })


def dashboard_admin(request):
    if request.session.get('rol') != 'admin':
        return redirect('login')

    datos = cargar_datos()

    return render(request, 'dashboardAdmin.html', {
        'nombre': request.session.get('nombre'),
        'total_estudiantes': len(datos["estudiantes"]),
        'total_tutores': len(datos["tutores"]),
        'total_cursos': len(datos["cursos"]),
    })