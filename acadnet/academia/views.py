from django.shortcuts import render, redirect
import xml.etree.ElementTree as ET
import os

RUTA_XML = os.path.join(os.path.dirname(__file__),'registro.xml')  # Se asigna una variable para asignar la ruta de base de la datos


def cargar_usuarios():  # se crea una funcion para asignar los datos del XML
    usuarios = {"estudiantes": {}, "tutores": {}}  # Se cargan los estudiantes y tutores

    if not os.path.exists(RUTA_XML):  # Si el archivo de la base de datos no existe o se encuentra en otra ruta
        print(f" No se encuentra {RUTA_XML}")  # imprime la ubicacion actual del archivo
        return usuarios

    tree = ET.parse(RUTA_XML)  # Funciones propias de la libreria elementTree
    root = tree.getroot()  # Funciones propias de la libreria elementTree

    # Cargar estudiantes (usuario = carnet)
    for est in root.findall(".//estudiante"):
        carnet = est.get("carnet")  # Se usa el Numero de carnet como usuario para iniciar secion
        usuarios["estudiantes"][carnet] = {
            "nombre": est.text,
            "contrasenia": est.get("contrasenia")
        }

        # Cargar tutores (usuario = registro_personal)
    for tut in root.findall(".//tutor"):
        registro = tut.get("registro_personal")  # Se usa el registro_personal como usuario para iniciar secion
        usuarios["tutores"][registro] = {
            "nombre": tut.text,
            "contrasenia": tut.get("contrasenia")
        }
    return usuarios


def login_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')  # Obtiene el usuario colocado para el inicio de secion
        contrasenia = request.POST.get('contrasenia')  # Obtiene la contraseña colocado para el inicio de secion

        usuarios = cargar_usuarios()  # Se llama a la funsion de cargar usuario para para validar el rol del
        # ingreso que se esta ingresando, se asigna a una variable para que este pueda ser validadacon los if

        # Condicional si el usuario llega a hacer el Admin
        if usuario == "AdminPPCYL2" and contrasenia == "AdminPPCYL2771":  # Credenciales dadas por defecto segun el cliente
            request.session['rol'] = 'admin'  # Se asigna el rol de Admin
            request.session['nombre'] = 'Administrador del Sistema'
            request.session['usuario'] = usuario
            return redirect('admin')

        # Condicional si el usuario llega a ser un estudiante
        if usuario in usuarios[
            "estudiantes"]:  # Se verifica si el usuario asignado pertenece a estudiantes, de no ser asi pasa al siguiente if de tutores
            if contrasenia == usuarios["estudiantes"][usuario][
                "contrasenia"]:  # Despues de validar usuario valida la contraseña
                request.session['rol'] = 'estudiante'  # Se le agrega un rol de estudiante
                request.session['nombre'] = usuarios["estudiantes"][usuario]["nombre"]
                request.session['carnet'] = usuario
                return redirect('student')

        # Condicional si el usuario llega a ser un tutor
        if usuario in usuarios[
            "tutores"]:  # Se verifica si el usuario asignado pertenece a tutores, de no ser asi pasa al siguiente if de usuario erroneo
            if contrasenia == usuarios["tutores"][usuario][
                "contrasenia"]:  # Despues de validar usuario valida la contraseña
                request.session['rol'] = 'tutor'  # Se le agrega un rol de tutor
                request.session['nombre'] = usuarios["tutores"][usuario]["nombre"]
                request.session['registro'] = usuario
                return redirect('tutor')

    return redirect('login')


def dashboard_student(request):
    """Panel del Estudiante"""
    if request.session.get('rol') != 'estudiante':
        return redirect('login')
    return render(request, 'dashboardStudent.html', {
        'nombre': request.session.get('nombre'),
        'carnet': request.session.get('carnet')
    })


def dashboard_admin(request):
    """Panel del Administrador"""
    if request.session.get('rol') != 'admin':
        return redirect('login')
    return render(request, 'dashboardAdmin.html', {
        'nombre': request.session.get('nombre'),
        'usuario': request.session.get('usuario')
    })


def dashboard_tutor(request):
    """Panel del Tutor"""
    if request.session.get('rol') != 'tutor':
        return redirect('login')
    return render(request, 'dashboardTutor.html', {
        'nombre': request.session.get('nombre'),
        'registro': request.session.get('registro')
    })
