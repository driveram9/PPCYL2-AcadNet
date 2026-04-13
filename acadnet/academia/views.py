from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests
import json

# ============================================
# CONFIGURACIÓN DEL BACKEND
# ============================================
BACKEND_URL = "http://localhost:5000/api"


# ============================================
# FUNCIONES DE LOGIN Y AUTENTICACIÓN
# ============================================

def login_view(request):
    """Vista de login - maneja autenticación de usuarios"""
    mensaje_error = None

    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasenia = request.POST.get('contrasenia')

        print(f"🔍 Django recibió: usuario={usuario}")

        # 1. VERIFICAR ADMIN (local en Django)
        if usuario == "AdminPPCYL2" and contrasenia == "AdminPPCYL2771":
            print("✅ Admin validado localmente")
            request.session['rol'] = 'admin'
            request.session['nombre'] = 'Administrador del Sistema'
            request.session['usuario'] = usuario
            return redirect('admin_dashboard')

        # 2. CONSULTAR AL BACKEND FLASK
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
                    else:
                        mensaje_error = f"Rol '{rol}' no reconocido"
                else:
                    mensaje_error = data.get("mensaje", "Credenciales incorrectas")
            else:
                mensaje_error = f"Error en el servidor"

        except requests.exceptions.ConnectionError:
            mensaje_error = "❌ Error de conexión con el servidor"
        except Exception as e:
            mensaje_error = f"❌ Error: {str(e)}"

        if mensaje_error:
            return render(request, "login.html", {"error": mensaje_error})

    return render(request, "login.html")


def logout_view(request):
    """Cerrar sesión"""
    request.session.flush()
    return redirect('login')


# ============================================
# DASHBOARDS
# ============================================

def admin_dashboard(request):
    """Dashboard para administrador"""
    if request.session.get('rol') != 'admin':
        return redirect('login')

    context = {
        'nombre': request.session.get('nombre', 'Administrador'),
        'usuario': request.session.get('usuario', ''),
    }
    return render(request, 'dashboardAdmin.html', context)


def estudiante_dashboard(request):
    """Dashboard para estudiantes"""
    if request.session.get('rol') != 'estudiante':
        return redirect('login')

    context = {
        'nombre': request.session.get('nombre', 'Estudiante'),
        'carnet': request.session.get('carnet', ''),
    }
    return render(request, 'dashboardStudent.html', context)


def tutor_dashboard(request):
    """Dashboard principal del tutor"""
    if request.session.get('rol') != 'tutor':
        return redirect('login')

    registro = request.session.get('registro')
    nombre = request.session.get('nombre')

    # Obtener cursos del tutor
    cursos = []
    try:
        response = requests.get(f"{BACKEND_URL}/cursos/{registro}", timeout=5)
        if response.status_code == 200:
            cursos = response.json()
    except Exception as e:
        print(f"Error al obtener cursos: {e}")

    context = {
        'nombre': nombre,
        'registro': registro,
        'cursos': cursos
    }
    return render(request, 'dashboardTutor.html', context)


# ============================================
# APIS PARA EL TUTOR
# ============================================

@csrf_exempt
def api_tutor_horarios(request):
    """API para obtener horarios del tutor"""
    if request.session.get('rol') != 'tutor':
        return JsonResponse({'error': 'No autorizado'}, status=403)

    registro = request.session.get('registro')

    if request.method == 'GET':
        try:
            response = requests.get(f"{BACKEND_URL}/horarios/{registro}", timeout=5)
            if response.status_code == 200:
                return JsonResponse(response.json(), safe=False)
            return JsonResponse([], safe=False)
        except Exception as e:
            return JsonResponse([], safe=False)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def api_tutor_limpiar_horarios(request):
    """API para limpiar todos los horarios del tutor"""
    if request.session.get('rol') != 'tutor':
        return JsonResponse({'error': 'No autorizado'}, status=403)

    registro = request.session.get('registro')

    if request.method == 'DELETE':
        try:
            response = requests.delete(f"{BACKEND_URL}/horarios/limpiar/{registro}", timeout=5)
            if response.status_code == 200:
                return JsonResponse({'success': True, 'mensaje': 'Horarios eliminados'})
            return JsonResponse({'success': False, 'error': 'Error en el backend'}, status=500)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def api_tutor_cargar_horarios(request):
    """API para subir archivo de horarios XML"""
    if request.session.get('rol') != 'tutor':
        return JsonResponse({'error': 'No autorizado'}, status=403)

    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        registro = request.session.get('registro')

        try:
            files = {'archivo_horarios': archivo}
            response = requests.post(
                f"{BACKEND_URL}/horarios/cargar/{registro}",
                files=files,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                return JsonResponse({'success': True, 'mensaje': data.get('mensaje', 'Horarios cargados')})
            else:
                return JsonResponse({'success': False, 'error': 'Error en el backend'}, status=500)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def api_tutor_notas(request):
    """API para subir archivo de notas XML"""
    if request.session.get('rol') != 'tutor':
        return JsonResponse({'error': 'No autorizado'}, status=403)

    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        registro = request.session.get('registro')

        try:
            files = {'archivo_notas': archivo}
            response = requests.post(
                f"{BACKEND_URL}/notas/{registro}",
                files=files,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                return JsonResponse({'success': True, 'mensaje': data.get('mensaje', 'Notas cargadas')})
            else:
                return JsonResponse({'success': False, 'error': 'Error en el backend'}, status=500)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def api_tutor_reportes(request):
    """API para obtener datos de reportes"""
    if request.session.get('rol') != 'tutor':
        return JsonResponse({'error': 'No autorizado'}, status=403)

    registro = request.session.get('registro')

    try:
        response = requests.get(f"{BACKEND_URL}/reportes/{registro}", timeout=5)
        if response.status_code == 200:
            return JsonResponse(response.json())
        return JsonResponse({'actividades': [], 'promedios': {}, 'top_data': {}})
    except Exception as e:
        return JsonResponse({'actividades': [], 'promedios': {}, 'top_data': {}})