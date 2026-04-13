from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def login_api(request):
    usuario = request.data.get('usuario')
    contrasenia = request.data.get('contrasenia')

    if usuario == "student" and contrasenia == "1234":
        return Response({"status": "ok", "rol": "student"})

    elif usuario == "admin" and contrasenia == "1234":
        return Response({"status": "ok", "rol": "admin"})

    elif usuario == "tutor" and contrasenia == "1234":
        return Response({"status": "ok", "rol": "tutor"})

    else:
        return Response({"status": "error", "mensaje": "Credenciales incorrectas"})