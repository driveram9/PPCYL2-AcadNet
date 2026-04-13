# services-matriz.py
# Módulo encargado de manejar la matriz dispersa de notas y generar reportes.

import statistics

class MatrizDispersa:
    """
    Clase que representa una matriz dispersa para almacenar notas de estudiantes.
    Filas = actividades (ej. Tarea1, Examen1)
    Columnas = carnets de estudiantes
    Valores = notas (0–100)
    """

    def __init__(self):
        # Diccionario con clave = (actividad, carnet), valor = nota
        self.valores = {}

    def insertar_nota(self, actividad: str, carnet: str, nota: int):
        """
        Inserta una nota en la matriz dispersa validando rango.
        """
        if 0 <= nota <= 100:
            self.valores[(actividad, carnet)] = nota
        else:
            print(f"Nota inválida para {carnet} en {actividad}: {nota}")

    def obtener_nota(self, actividad: str, carnet: str):
        """
        Devuelve la nota de un estudiante en una actividad específica.
        """
        return self.valores.get((actividad, carnet), None)

    def obtener_por_actividad(self, actividad: str):
        """
        Devuelve todas las notas de una actividad.
        """
        return {c: n for (a, c), n in self.valores.items() if a == actividad}

    def obtener_por_estudiante(self, carnet: str):
        """
        Devuelve todas las notas de un estudiante.
        """
        return {a: n for (a, c), n in self.valores.items() if c == carnet}


class ReporteNotas:
    """
    Clase encargada de generar reportes a partir de la matriz dispersa.
    """

    def __init__(self, matriz: MatrizDispersa):
        self.matriz = matriz

    def promedio_por_actividad(self, actividad: str) -> float:
        """
        Calcula el promedio de notas de una actividad.
        """
        notas = list(self.matriz.obtener_por_actividad(actividad).values())
        return statistics.mean(notas) if notas else 0

    def top_notas_actividad(self, actividad: str):
        """
        Devuelve las notas ordenadas de mayor a menor para una actividad.
        """
        notas = self.matriz.obtener_por_actividad(actividad)
        return dict(sorted(notas.items(), key=lambda x: x[1], reverse=True))