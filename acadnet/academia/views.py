from django.shortcuts import render, redirect
import requests

BACKEND_URL = "http://127.0.0.1:5000"  # Ajusta al puerto de tu Flask

def login_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasenia = request.POST.get('contrasenia')

        # Enviar credenciales al backend
        response = requests.post(f"{BACKEND_URL}/login",
                                 json={"usuario": usuario, "contrasenia": contrasenia})
        data = response.json()

        if data.get("status") == "ok":
            rol = data.get("rol")
            nombre = data.get("nombre")

            request.session['rol'] = rol
            request.session['nombre'] = nombre
            request.session['usuario'] = usuario

            if rol == "admin":
                return redirect('admin_dashboard')
            elif rol == "estudiante":
                request.session['carnet'] = data.get("carnet")
                return redirect('student')
            elif rol == "tutor":
                request.session['registro'] = data.get("registro_personal")
                return redirect('tutor')

    return render(request, "login.html")
