import requests
from django.shortcuts import render, redirect

def login_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasenia = request.POST.get('contrasenia')

        # Llamada al backend Flask
        response = requests.post("http://localhost:5000/api/login", json={
            "usuario": usuario,
            "contrasenia": contrasenia
        })

        data = response.json()

        if data.get("status") == "ok":
            rol = data.get("rol")

            if rol == "estudiante":
                request.session["nombre"] = data.get("nombre")
                request.session["carnet"] = data.get("carnet")
                return redirect('student')

            elif rol == "admin":
                return redirect('admin')

            elif rol == "tutor":
                return redirect('dashboard_tutor')

        else:
            return render(request, 'login.html', {
                'error': data.get("mensaje", "Usuario o contraseña incorrecta")
            })

    return render(request, 'login.html')
