from django.shortcuts import render, redirect
import xml.etree.ElementTree as ET
import os

RUTA_XML = os.path.join(os.path.dirname(__file__), 'registro.xml')


def cargar_usuarios():
    usuarios = {"estudiantes": {}, "tutores": {}}

    if not os.path.exists(RUTA_XML):
        print(f"No se encuentra {RUTA_XML}")
        return usuarios

    tree = ET.parse(RUTA_XML)
    root = tree.getroot()

    # Cargar estudiantes
    for est in root.findall(".//estudiante"):
        carnet = est.get("carnet")
        usuarios["estudiantes"][carnet] = {
            "nombre": est.text,
            "contrasenia": est.get("contrasenia")
        }

    # Cargar tutores
    for tut in root.findall(".//tutor"):
        registro = tut.get("registro_personal")
        usuarios["tutores"][registro] = {
            "nombre": tut.text,
            "contrasenia": tut.get("contrasenia")
        }
    return usuarios


def login_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasenia = request.POST.get('contrasenia')

        usuarios = cargar_usuarios()

        # Admin
        if usuario == "AdminPPCYL2" and contrasenia == "AdminPPCYL2771":
            request.session['rol'] = 'admin'
            request.session['nombre'] = 'Administrador del Sistema'
            request.session['usuario'] = usuario
            return redirect('admin_dashboard')

        # Estudiante
        if usuario in usuarios["estudiantes"]:
            if contrasenia == usuarios["estudiantes"][usuario]["contrasenia"]:
                request.session['rol'] = 'estudiante'
                request.session['nombre'] = usuarios["estudiantes"][usuario]["nombre"]
                request.session['carnet'] = usuario
                return redirect('student')

        # Tutor
        if usuario in usuarios["tutores"]:
            if contrasenia == usuarios["tutores"][usuario]["contrasenia"]:
                request.session['rol'] = 'tutor'
                request.session['nombre'] = usuarios["tutores"][usuario]["nombre"]
                request.session['registro'] = usuario
                return redirect('tutor')

    return render(request, "login.html")


def estudiante_dashboard(request):
    if request.session.get('rol') != 'estudiante':
        return redirect('login')
    return render(request, 'dashboardStudent.html', {
        'nombre': request.session.get('nombre'),
        'carnet': request.session.get('carnet')
    })


def admin_dashboard(request):
    if request.session.get('rol') != 'admin':
        return redirect('login')
    return render(request, 'dashboardAdmin.html', {
        'nombre': request.session.get('nombre'),
        'usuario': request.session.get('usuario')
    })


def tutor_dashboard(request):
    if request.session.get('rol') != 'tutor':
        return redirect('login')
    return render(request, 'dashboardTutor.html', {
        'nombre': request.session.get('nombre'),
        'registro': request.session.get('registro')
    })
