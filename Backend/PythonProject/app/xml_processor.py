# services-xml_processor.py
# Módulo encargado de procesar archivos XML de entrada y salida
# para cursos, tutores y estudiantes.

import xml.etree.ElementTree as ET
import json

class XMLProcessor:
    """
    Clase para manejar la lectura, validación y transformación de archivos XML.
    """

    def __init__(self, ruta_archivo: str):
        self.ruta_archivo = ruta_archivo
        self.tree = None
        self.root = None

    def cargar_xml(self):
        """
        Carga el archivo XML desde la ruta especificada.
        """
        try:
            self.tree = ET.parse(self.ruta_archivo)
            self.root = self.tree.getroot()
            return True
        except Exception as e:
            print(f"Error al cargar XML: {e}")
            return False

    def xml_a_json(self):
        """
        Convierte el XML cargado en un diccionario JSON estandarizado.
        """
        if self.root is None:
            return {}

        def recorrer(elemento):
            # Convierte recursivamente un nodo XML en dict
            nodo = {}
            for child in elemento:
                if len(child) > 0:
                    nodo[child.tag] = recorrer(child)
                else:
                    nodo[child.tag] = child.text if child.text else ""
                # Agregar atributos si existen
                if child.attrib:
                    nodo[child.tag + "_atributos"] = child.attrib
            return nodo

        return recorrer(self.root)

    def validar_configuraciones(self):
        """
        Valida que los cursos, tutores y estudiantes tengan la estructura correcta.
        """
        if self.root is None:
            return False

        cursos = self.root.find("cursos")
        tutores = self.root.find("tutores")
        estudiantes = self.root.find("estudiantes")

        if cursos is None or tutores is None or estudiantes is None:
            print("Error: faltan secciones en el XML.")
            return False

        return True

    def generar_xml_salida(self, tutores_cargados, estudiantes_cargados,
                           asignaciones_tutores, asignaciones_estudiantes,
                           archivo_salida="salida.xml"):
        """
        Genera un archivo XML de salida con la estructura definida en el enunciado.
        """
        configuraciones_aplicadas = ET.Element("configuraciones_aplicadas")

        # Totales
        ET.SubElement(configuraciones_aplicadas, "tutores_cargados").text = str(tutores_cargados)
        ET.SubElement(configuraciones_aplicadas, "estudiantes_cargados").text = str(estudiantes_cargados)

        # Asignaciones
        asignaciones = ET.SubElement(configuraciones_aplicadas, "asignaciones")

        tutores = ET.SubElement(asignaciones, "tutores")
        ET.SubElement(tutores, "total").text = str(asignaciones_tutores.get("total", 0))
        ET.SubElement(tutores, "correcto").text = str(asignaciones_tutores.get("correcto", 0))
        ET.SubElement(tutores, "incorrecto").text = str(asignaciones_tutores.get("incorrecto", 0))

        estudiantes = ET.SubElement(asignaciones, "estudiantes")
        ET.SubElement(estudiantes, "total").text = str(asignaciones_estudiantes.get("total", 0))
        ET.SubElement(estudiantes, "correcto").text = str(asignaciones_estudiantes.get("correcto", 0))
        ET.SubElement(estudiantes, "incorrecto").text = str(asignaciones_estudiantes.get("incorrecto", 0))

        # Guardar archivo
        tree = ET.ElementTree(configuraciones_aplicadas)
        tree.write(archivo_salida, encoding="utf-8", xml_declaration=True)
        print(f"Archivo de salida generado: {archivo_salida}")