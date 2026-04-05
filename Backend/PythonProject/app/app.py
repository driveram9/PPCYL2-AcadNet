#Se importan las librerias que se usaran para que el back end funcione
from flask import Flask, render_template, request, url_for, redirect, session #Exportamos la libreria Flask encafgado del pensamiento logico
import xml.etree.ElementTree as ET #Extraer archivos del XML para ser usados en el Backend
import os #Comprobar que el archivo XML es existente y saber su ubicacion

#Lineas necesarias para extraer las paginas necesarias para la interfaz grafica y resguardo de claves
app = Flask(__name__, template_folder="templates", static_folder="static")#Extrae las estructuras del programa
app.secret_key = "clave_para_flask" #Seguridad en contraseñas

#Funciones para extraer los datos del programa XML y cargarlos a la aplicacion
def cargar_usuarios():
    usuarios = []
    ruta_xml = "Base.xml"

    if not os.path.exists(ruta_xml):#Verificacion si el archivo existe #
        print(f" ERROR: No se encuentra el archivo {ruta_xml}")#Mensiona en que ruta estaba guardado el archivo
        print(f" Directorio actual: {os.getcwd()}") #Mensiona en que ruta se encuentra actualmente el archivo
        return usuarios

    try:
        # Extraer datos del XML
        tree = ET.parse(ruta_xml)
        root = tree.getroot()

        for usuario in root.findall(".//usuario"):#Genera un for para recorrer completamente la base de datos XML
            # Extraer datos
            datos = {
                "id": usuario.get("id", "0"), # extrae el ID se coloca 0 por defecto
                "nombre": usuario.findtext("nombre", "Sin nombre"),#Se extra los nombre
                "rol": usuario.findtext("rol", "sin_rol"),#Se extra los Roles asignados
                "login": usuario.findtext("login", ""),#Se extra los ingresos
                "contrasenia": usuario.findtext("contrasenia", ""),#Se extra las contraseñas de los ingresos
                "email": usuario.findtext("email", "no@email.com"),#Se extra los informacion adicional e-mail
                "estado": usuario.findtext("estado", "activo")#Usuario activo o inactivo
            }
            usuarios.append(datos) #Agrega los datos extraidos del XML al Arraid usuarios

    except ET.ParseError as e:#Se crea estas funciones con el objetivo de saber si los arxhivos extraidos tuvieron algun error
        print(f"Error al parsear XML: {e}")
    except Exception as e:#saber si ubo algun error en la extraccion de datos
        print(f"Error inesperado: {e}")
    return usuarios


def validar_login(usuario, contrasenia):#Validar las credenciales si son validas
    usuarios = cargar_usuarios()

    for user in usuarios:
        if user["login"] == usuario and user["contrasenia"] == contrasenia: #Login realizado
            # Verificar si el usuario está activo

            if user["estado"] == "activo":
                return user
            else:
                return {"error": "usuario_inactivo"}

    return None


@app.route("/")
def index():
    if session.get("usuario_rol"):#Extraer el Rol correspondiente de cada usuario
        rol = session.get("usuario_rol") #Rol asignado a la variable rol
        if rol == "administrador": #Validacion de rol de administrador
            return redirect(url_for("admin_dashboard")) #Dirigido al dashboard de admin
        elif rol == "tutor": #Validacion del rol de Tutor
            return redirect(url_for("tutor_dashboard")) #Dirigido al dashboard de tutor
        elif rol == "estudiante":#Validacion del rol de Estudiante
            return redirect(url_for("estudiante_dashboard")) #redirigido al dashboar de estudiante

    return render_template("index.html")#inicia la pagina de inicio de secion

@app.route("/login", methods=["POST"])
def login():
    usuario = request.form.get('usuario','') #Se obtienen los datos de usuario de la interfaz grafica
    contrasenia = request.form.get('contrasenia','')#Se obtienen los datos de contraseña de la interfaz grafica

    if not usuario or not contrasenia: #hacer cuando no se cuenta con usuario o sin contraseña
        return render_template("index.html", error=" Por favor, complete todos los campos")

    # Validar credenciales
    resultado = validar_login(usuario, contrasenia)

    if resultado is None: #Cuando el usuario ni la contraseña con encontrados en la base de datos
        return render_template("index.html", error=" Usuario o contraseña incorrectos")

    if isinstance(resultado, dict) and resultado.get("error") == "usuario_inactivo": #Cuando el usuario esta bloqueado
        return render_template("index.html", error=" Su cuenta está inactiva. Contacte al administrador.")

    #En este caso no es necesario usar otro if para validar que existe el usuario ya que anteriormente los agarraria los fi colocados.
    #Una vez pasados los If que retienen los usuarios no valiodos se procede a guardarlos en las variables correspondientes para ser usados en el programa
    session["usuario_id"] = resultado["id"]
    session["usuario_nombre"] = resultado["nombre"]
    session["usuario_rol"] = resultado["rol"]
    session["usuario_login"] = resultado["login"]
    session["usuario_email"] = resultado["email"]

    #Se crea la variable rolpara poder redirigirlos segun su rol a la pagina correspondiente
    rol = resultado["rol"]

    if rol == "administrador": #Dirige al rol de admin
        return redirect(url_for("admin_dashboard"))
    elif rol == "tutor":#Dirige al rol de tutor
        return redirect(url_for("tutor_dashboard"))
    elif rol == "estudiante":#Dirige al rol de estudiante
        return redirect(url_for("estudiante_dashboard"))
    else: #se usara un else para cuando una persona en la base de datos no cuente con un rol asignado
        return render_template("index.html", error=f" Rol '{rol}' no reconocido")



@app.route("/admin")
def admin_dashboard():
    return render_template("admin.html")



if __name__ == '__main__':
    app.run(debug=True, port=5000)
