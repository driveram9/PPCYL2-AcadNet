# Matriz Dispersa
class MatrizDispersa:
    def __init__(self):
        # Diccionario con clave = (actividad, carnet), valor = nota
        self.valores = {}

    def insertar_nota(self, actividad, carnet, nota):
        # Validar rango de nota
        if 0 <= nota <= 100:
            self.valores[(actividad, carnet)] = nota

    def obtener_nota(self, actividad, carnet):
        return self.valores.get((actividad, carnet), None)

    def obtener_por_actividad(self, actividad):
        # Devuelve todas las notas de una actividad
        return {c: n for (a, c), n in self.valores.items() if a == actividad}

    def obtener_por_estudiante(self, carnet):
        # Devuelve todas las notas de un estudiante
        return {a: n for (a, c), n in self.valores.items() if c == carnet}

    ## Reportes de Notas

import statistics

class ReporteNotas:
        def __init__(self, matriz):
            self.matriz = matriz

        def promedio_por_actividad(self, actividad):
            notas = list(self.matriz.obtener_por_actividad(actividad).values())
            return statistics.mean(notas) if notas else 0

        def top_notas_actividad(self, actividad):
            notas = self.matriz.obtener_por_actividad(actividad)
            # Ordenar de mayor a menor
            return dict(sorted(notas.items(), key=lambda x: x[1], reverse=True))