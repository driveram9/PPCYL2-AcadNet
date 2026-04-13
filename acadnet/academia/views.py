from django.shortcuts import render, redirect
from django.urls import reverse
import requests
import json
import os
import xml.etree.ElementTree as ET

BACKEND_URL = "http://localhost:5000/api"


def login_view(request):
    mensaje_error = None

    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasenia = request.POST.get('contrasenia')

        print(f"🔍 Django recibió: usuario={usuario}")

        # Validar admin local
        if usuario == "AdminPPCYL2" and contrasenia == "AdminPPCYL2771":
            request.session['rol'] = 'admin'
            request.session['nombre'] = 'Administrador del Sistema'
            request.session['usuario'] = usuario
            return redirect('admin_dashboard')

        try:
            response = requests.post(
                f"{BACKEND_URL}/login",
                json={"usuario": usuario, "contrasenia": contrasenia},
                timeout=5,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                data = response.json()

                if data.get("success"):
                    rol = data.get("rol")
                    nombre = data.get("nombre")

                    request.session['rol'] = rol
                    request.session['nombre'] = nombre

                    if rol == 'tutor':
                        request.session['registro'] = usuario
                        return redirect('tutor_dashboard')
                    elif rol == 'estudiante':
                        request.session['carnet'] = usuario
                        return redirect('estudiante_dashboard')
                    elif rol == 'admin':
                        return redirect('admin_dashboard')
                else:
                    mensaje_error = data.get("mensaje", "Credenciales incorrectas")
            else:
                mensaje_error = f"Error en servidor: {response.status_code}"

        except requests.exceptions.ConnectionError:
            mensaje_error = "Error de conexión con el servidor"
        except Exception as e:
            # NO imprimir el error de Django, solo el nuestro
            print(f"❌ Error en login: {e}")
            mensaje_error = "Error interno del servidor"

        if mensaje_error:
            return render(request, "login.html", {"error": mensaje_error})

    return render(request, "login.html")


def estudiante_dashboard(request):
    """Dashboard para estudiantes"""
    # Verificar autenticación
    if request.session.get('rol') != 'estudiante':
        return redirect('login')

    context = {
        'nombre': request.session.get('nombre', 'Estudiante'),
        'carnet': request.session.get('carnet', ''),
        'rol': request.session.get('rol', '')
    }
    return render(request, 'dashboardStudent.html', context)


def admin_dashboard(request):
    """Dashboard para administrador"""
    # Verificar autenticación
    if request.session.get('rol') != 'admin':
        return redirect('login')

    context = {
        'nombre': request.session.get('nombre', 'Administrador'),
        'usuario': request.session.get('usuario', ''),
        'rol': request.session.get('rol', '')
    }
    return render(request, 'dashboardAdmin.html', context)


def tutor_dashboard(request):
    """Dashboard para tutores"""
    # Verificar autenticación
    if request.session.get('rol') != 'tutor':
        print(f"⚠️ Acceso denegado: rol={request.session.get('rol')}, esperaba tutor")
        return redirect('login')

    registro = request.session.get('registro')
    nombre = request.session.get('nombre')

    print(f"📚 Cargando dashboard de tutor: {nombre} (registro: {registro})")

    # Obtener cursos del tutor desde el backend
    cursos = []
    try:
        response = requests.get(
            f"{BACKEND_URL}/cursos/{registro}",
            timeout=5
        )
        if response.status_code == 200:
            cursos = response.json()
            print(f"📌 Cursos encontrados: {cursos}")
    except Exception as e:
        print(f"⚠️ Error al obtener cursos: {e}")

    context = {
        'nombre': nombre,
        'registro': registro,
        'rol': 'tutor',
        'cursos': cursos
    }
    return render(request, 'dashboardTutor.html', context)


def logout_view(request):
    """Cerrar sesión"""
    request.session.flush()
    return redirect('login')