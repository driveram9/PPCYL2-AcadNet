from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests

BACKEND_URL = "http://localhost:5000/api"


def login_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasenia = request.POST.get('contrasenia')

        # Admin local
        if usuario == "AdminPPCYL2" and contrasenia == "AdminPPCYL2771":
            request.session['rol'] = 'admin'
            request.session['nombre'] = 'Administrador del Sistema'
            return redirect('admin_dashboard')

        # Consultar backend
        try:
            response = requests.post(f"{BACKEND_URL}/login", json={"usuario": usuario, "contrasenia": contrasenia},
                                     timeout=5)
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
        except:
            pass

        return render(request, "login.html", {"error": "Credenciales incorrectas"})

    return render(request, "login.html")


def logout_view(request):
    request.session.flush()
    return redirect('login')


def admin_dashboard(request):
    if request.session.get('rol') != 'admin':
        return redirect('login')
    return render(request, 'dashboardAdmin.html', {'nombre': request.session.get('nombre')})


def estudiante_dashboard(request):
    if request.session.get('rol') != 'estudiante':
        return redirect('login')
    return render(request, 'dashboardStudent.html',
                  {'nombre': request.session.get('nombre'), 'carnet': request.session.get('carnet')})


def tutor_dashboard(request):
    if request.session.get('rol') != 'tutor':
        return redirect('login')

    registro = request.session.get('registro')
    cursos = []
    try:
        response = requests.get(f"{BACKEND_URL}/cursos/{registro}", timeout=5)
        if response.status_code == 200:
            cursos = response.json()
    except:
        pass

    return render(request, 'dashboardTutor.html', {
        'nombre': request.session.get('nombre'),
        'registro': registro,
        'cursos': cursos
    })

@csrf_exempt
def api_tutor_horarios(request):
    if request.session.get('rol') != 'tutor':
        return JsonResponse({'error': 'No autorizado'}, status=403)

    registro = request.session.get('registro')

    if request.method == 'GET':
        try:
            response = requests.get(f"{BACKEND_URL}/horarios/{registro}", timeout=5)
            return JsonResponse(response.json() if response.status_code == 200 else [], safe=False)
        except:
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
                data = response.json()
                return JsonResponse(
                    {'success': data.get('success', True), 'mensaje': data.get('mensaje', 'Horarios eliminados')})
            return JsonResponse({'success': False, 'error': 'Error en el backend'}, status=500)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def api_tutor_cargar_horarios(request):
    if request.session.get('rol') != 'tutor':
        return JsonResponse({'error': 'No autorizado'}, status=403)

    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        registro = request.session.get('registro')

        try:
            files = {'archivo_horarios': archivo}
            response = requests.post(f"{BACKEND_URL}/horarios/cargar/{registro}", files=files, timeout=30)
            return JsonResponse(response.json() if response.status_code == 200 else {'success': False})
        except:
            return JsonResponse({'success': False, 'error': 'Error de conexión'}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def api_tutor_notas(request):
    if request.session.get('rol') != 'tutor':
        return JsonResponse({'error': 'No autorizado'}, status=403)

    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        registro = request.session.get('registro')

        try:
            files = {'archivo_notas': archivo}
            response = requests.post(f"{BACKEND_URL}/notas/{registro}", files=files, timeout=30)
            return JsonResponse(response.json() if response.status_code == 200 else {'success': False})
        except:
            return JsonResponse({'success': False, 'error': 'Error de conexión'}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def api_tutor_reportes(request):
    if request.session.get('rol') != 'tutor':
        return JsonResponse({'error': 'No autorizado'}, status=403)

    registro = request.session.get('registro')

    try:
        response = requests.get(f"{BACKEND_URL}/reportes/{registro}", timeout=5)
        return JsonResponse(
            response.json() if response.status_code == 200 else {'actividades': [], 'promedios': {}, 'top_data': {}})
    except:
        return JsonResponse({'actividades': [], 'promedios': {}, 'top_data': {}})

@csrf_exempt
def api_estudiante_cursos(request, carnet):
    """Obtener cursos del estudiante"""
    if request.session.get('rol') != 'estudiante':
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        response = requests.get(f"{BACKEND_URL}/estudiante/cursos/{carnet}", timeout=5)
        if response.status_code == 200:
            return JsonResponse(response.json(), safe=False)
        return JsonResponse([], safe=False)
    except Exception as e:
        return JsonResponse([], safe=False)


@csrf_exempt
def api_estudiante_tareas(request, carnet):
    """Obtener tareas del estudiante"""
    if request.session.get('rol') != 'estudiante':
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        response = requests.get(f"{BACKEND_URL}/estudiante/tareas/{carnet}", timeout=5)
        if response.status_code == 200:
            return JsonResponse(response.json(), safe=False)
        return JsonResponse([], safe=False)
    except Exception as e:
        return JsonResponse([], safe=False)


@csrf_exempt
def api_estudiante_notas(request, carnet):
    """Obtener notas del estudiante"""
    if request.session.get('rol') != 'estudiante':
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        response = requests.get(f"{BACKEND_URL}/estudiante/notas/{carnet}", timeout=5)
        if response.status_code == 200:
            return JsonResponse(response.json())
        return JsonResponse({'notas': [], 'cursos': {}})
    except Exception as e:
        return JsonResponse({'notas': [], 'cursos': {}})


@csrf_exempt
def api_estudiante_anuncios(request):
    """Obtener anuncios generales"""
    if request.session.get('rol') != 'estudiante':
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        response = requests.get(f"{BACKEND_URL}/anuncios", timeout=5)
        if response.status_code == 200:
            return JsonResponse(response.json(), safe=False)
        return JsonResponse([], safe=False)
    except Exception as e:
        return JsonResponse([], safe=False)


@csrf_exempt
def api_estudiante_horarios(request):
    """Obtener horarios de tutoría"""
    if request.session.get('rol') != 'estudiante':
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        response = requests.get(f"{BACKEND_URL}/horarios/todos", timeout=5)
        if response.status_code == 200:
            return JsonResponse(response.json(), safe=False)
        return JsonResponse([], safe=False)
    except Exception as e:
        return JsonResponse([], safe=False)
#Arrancar el frontend
#cd acadnet
#python manage.py runserver
