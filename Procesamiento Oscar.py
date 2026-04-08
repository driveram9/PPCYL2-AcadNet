class Nodo:
    def __init__(self, fila, columna, valor):
        self.fila = fila  # actividad
        self.columna = columna  # carnet
        self.valor = valor  # nota

        self.derecha = None
        self.abajo = None


class MatrizDispersa:
    def __init__(self):
        self.filas = {}  # actividades
        self.columnas = {}  # estudiantes

    def insertar(self, actividad, carnet, nota):
        if nota < 0 or nota > 100:
            print("Nota inválida")
            return

        # 🔥 ACTUALIZAR si ya existe
        if actividad in self.filas:
            actual = self.filas[actividad]
            while actual:
                if actual.columna == carnet:
                    actual.valor = nota
                    return
                actual = actual.derecha

        nuevo = Nodo(actividad, carnet, nota)

        # insertar en filas
        if actividad not in self.filas:
            self.filas[actividad] = nuevo
        else:
            actual = self.filas[actividad]
            while actual.derecha:
                actual = actual.derecha
            actual.derecha = nuevo

        # insertar en columnas
        if carnet not in self.columnas:
            self.columnas[carnet] = nuevo
        else:
            actual = self.columnas[carnet]
            while actual.abajo:
                actual = actual.abajo
            actual.abajo = nuevo

    def mostrar(self):
        for actividad in self.filas:
            actual = self.filas[actividad]
            print(f"Actividad: {actividad}")
            while actual:
                print(f"  Carnet: {actual.columna} Nota: {actual.valor}")
                actual = actual.derecha

    def promedio_por_actividad(self, actividad):
        if actividad not in self.filas:
            return 0

        actual = self.filas[actividad]
        suma = 0
        contador = 0

        while actual:
            suma += actual.valor
            contador += 1
            actual = actual.derecha

        return suma / contador if contador > 0 else 0

    def nota_maxima(self, actividad):
        if actividad not in self.filas:
            return None

        actual = self.filas[actividad]
        max_nota = -1

        while actual:
            if actual.valor > max_nota:
                max_nota = actual.valor
            actual = actual.derecha

        return max_nota

    # 🔥 TOP de notas ordenado
    def top_notas(self, actividad):
        if actividad not in self.filas:
            return []

        actual = self.filas[actividad]
        lista = []

        while actual:
            lista.append((actual.columna, actual.valor))
            actual = actual.derecha

        lista.sort(key=lambda x: x[1], reverse=True)
        return lista


import xml.etree.ElementTree as ET


def leer_xml(ruta, matriz_dispersa):
    tree = ET.parse(ruta)
    root = tree.getroot()

    # 🔥 buscar <notas>
    notas = root.find("notas")
    if notas is None:
        print("No se encontró <notas>")
        return

    for actividad in notas.findall("actividad"):
        nombre = actividad.get("nombre")
        carnet = actividad.get("carnet")

        texto = actividad.text

        if texto is None:
            print("Nota vacía")
            continue

        try:
            nota = int(texto)
        except ValueError:
            print("Nota inválida")
            continue

        matriz_dispersa.insertar(nombre, carnet, nota)


import re


def extraer_horario(texto):
    patron = r"HorarioI:\s(\d{2}:\d{2})\sHorarioF:\s(\d{2}:\d{2})"
    resultado = re.search(patron, texto)

    if resultado:
        return resultado.group(1), resultado.group(2)
    return None


# 🔥 Código de prueba
matriz = MatrizDispersa()

# Ejemplo de uso:
# leer_xml("notas.xml", matriz)
# matriz.mostrar()

# print("Promedio:", matriz.promedio_por_actividad("Tarea1"))
# print("Máxima:", matriz.nota_maxima("Tarea1"))

# top = matriz.top_notas("Tarea1")
# print("TOP NOTAS:")
# for carnet, nota in top:
#     print(carnet, nota)