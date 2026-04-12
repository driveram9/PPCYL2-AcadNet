# services-reportes.py
# Módulo encargado de generar reportes estadísticos y gráficos
# a partir de la matriz dispersa de notas.

import statistics
import plotly.express as px
import plotly.io as pio

from services-matriz import MatrizDispersa

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

    def generar_grafico_promedio(self, curso_codigo: str, actividades: list):
        """
        Genera un gráfico de barras con el promedio de notas por actividad.
        """
        data = {
            "Actividad": [],
            "Promedio": []
        }
        for act in actividades:
            data["Actividad"].append(act)
            data["Promedio"].append(self.promedio_por_actividad(act))

        fig = px.bar(data, x="Actividad", y="Promedio",
                     title=f"Promedio de notas - Curso {curso_codigo}")
        return fig

    def generar_grafico_top(self, curso_codigo: str, actividad: str):
        """
        Genera un gráfico de barras con el ranking de notas de una actividad.
        """
        notas = self.top_notas_actividad(actividad)
        data = {
            "Carnet": list(notas.keys()),
            "Nota": list(notas.values())
        }

        fig = px.bar(data, x="Carnet", y="Nota",
                     title=f"Top notas - {actividad} (Curso {curso_codigo})")
        return fig

    def exportar_pdf(self, fig, nombre_archivo: str):
        """
        Exporta un gráfico a PDF.
        """
        pio.write_image(fig, nombre_archivo, format="pdf")