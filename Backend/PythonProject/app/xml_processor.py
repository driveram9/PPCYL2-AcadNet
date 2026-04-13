import xml.etree.ElementTree as ET
import os

def validar_login(usuario, contrasenia):
    ruta_xml = os.path.join(os.path.dirname(__file__), "../registro.xml")
    if not os.path.exists(ruta_xml):
        return None
    try:
        tree = ET.parse(ruta_xml)
        root = tree.getroot()
        for user in root.findall(".//usuario"):
            if user.findtext("login") == usuario and user.findtext("contrasenia") == contrasenia:
                if user.findtext("estado") == "activo":
                    return {
                        "id": user.get("id"),
                        "nombre": user.findtext("nombre"),
                        "rol": user.findtext("rol"),
                        "login": usuario,
                        "email": user.findtext("email")
                    }
                else:
                    return {"error": "usuario_inactivo"}
    except ET.ParseError:
        return None
    return None
