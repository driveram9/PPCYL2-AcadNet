from django.shortcuts import render, redirect
import requests
import json

BACKEND_URL = "http://localhost:5000/api"


def login_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasenia = request.POST.get('contrasenia')

        print(f"🔍 Django recibió: usuario={usuario}")

        # ========================================
        # 1. VERIFICAR ADMIN (local en Django)
        # ========================================
        if usuario == "AdminPPCYL2" and contrasenia == "AdminPPCYL2771":
            print("✅ Admin validado localmente")
            request.session['rol'] = 'admin'
            request.session['nombre'] = 'Administrador del Sistema'
            request.session['usuario'] = usuario
            return redirect('admin_dashboard')

        # ========================================
        # 2. CONSULTAR AL BACKEND FLASK
        # ========================================
        try:
            print(f"📡 Consultando backend: {BACKEND_URL}/login")

            response = requests.post(
                f"{BACKEND_URL}/login",
                json={"usuario": usuario, "contrasenia": contrasenia},
                timeout=5,
                headers={"Content-Type": "application/json"}
            )

            print(f"📡 Respuesta status: {response.status_code}")
            print(f"📡 Respuesta body: {response.text}")

            if response.status_code == 200:
                data = response.json()

                if data.get("success"):
                    rol = data.get("rol")
                    nombre = data.get("nombre")

                    print(f"✅ Login exitoso: {nombre} ({rol})")

                    request.session['rol'] = rol
                    request.session['nombre'] = nombre

                    if rol == "tutor":
                        request.session['registro'] = usuario
                        return redirect('tutor_dashboard')
                    elif rol == "estudiante":
                        request.session['carnet'] = usuario
                        return redirect('estudiante_dashboard')
                else:
                    print(f"❌ Login fallido: {data.get('mensaje')}")

        except requests.exceptions.ConnectionError:
            print("❌ No se pudo conectar al backend Flask")
            return render(request, "login.html", {"error": "❌ Error de conexión con el servidor"})
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return render(request, "login.html", {"error": f"❌ Error: {e}"})

        return render(request, "login.html", {"error": "❌ Usuario o contraseña incorrectos"})

    return render(request, "login.html")