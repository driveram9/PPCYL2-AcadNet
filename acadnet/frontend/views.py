from django.shortcuts import render, redirect

def login_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasenia = request.POST.get('contrasenia')

        if usuario == "student" and contrasenia == "1234":
            return redirect('student')

        elif usuario == "admin" and contrasenia == "1234":
            return redirect('admin')

        elif usuario == "tutor" and contrasenia == "1234":
            return redirect('tutor')

        else:
            return render(request, 'login.html', {
                'error': 'Usuario o contraseña incorrecta'
            })

    return render(request, 'login.html')

def dashboard_student(request):
    return render(request, 'dashboardStudent.html')

def dashboard_admin(request):
    return render(request, 'dashboardAdmin.html')

def dashboard_tutor(request):
    return render(request, 'dashboardTutor.html')

def upload_view(request):
    return render(request, 'upload.html')

def tabla_view(request):
    estudiantes = [
        {"carnet": "2023001", "nombre": "Juan Pérez", "curso": "Matemática", "nota": 85},
        {"carnet": "2023002", "nombre": "Ana López", "curso": "Física", "nota": 90},
        {"carnet": "2023003", "nombre": "Carlos Ruiz", "curso": "Química", "nota": 78},
    ]

def dashboard_tutor(request):
    horarios = [
        {"curso": "Matemática", "inicio": "09:40", "fin": "10:30"},
        {"curso": "Física", "inicio": "10:30", "fin": "11:20"},
        ]

    return render(request, 'dashboardTutor.html', {"horarios": horarios})