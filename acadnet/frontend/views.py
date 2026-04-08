from django.shortcuts import render, redirect

def login_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasenia = request.POST.get('contrasenia')

        if usuario == "admin" and contrasenia == "1234":
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {
                'error': 'Usuario o contraseña incorrecta'
            })

    return render(request, 'login.html')

def dashboard_view(request):
    return render(request, 'dashboard.html')

def upload_view(request):
    return render(request, 'upload.html')

def tabla_view(request):
    estudiantes = [
        {"carnet": "2023001", "nombre": "Juan Pérez", "curso": "Matemática", "nota": 85},
        {"carnet": "2023002", "nombre": "Ana López", "curso": "Física", "nota": 90},
        {"carnet": "2023003", "nombre": "Carlos Ruiz", "curso": "Química", "nota": 78},
    ]

    return render(request, 'tabla.html', {"estudiantes": estudiantes})