# matrices/matriz_dispersa.py
# Matriz dispersa para almacenar notas de estudiantes

class MatrizDispersa:
    """
    Clase que representa una matriz dispersa para almacenar notas de estudiantes.
    Filas = actividades (ej. Tarea1, Examen1)
    Columnas = carnets de estudiantes
    Valores = notas (0-100)
    """

    def __init__(self):
        # Diccionario con clave = (actividad, carnet), valor = nota
        self.datos = {}
        self.filas = set()    # Actividades
        self.columnas = set() # Carnets

    def agregar(self, actividad: str, carnet: str, nota: float) -> bool:
        """
        Inserta una nota en la matriz dispersa validando rango.
        Retorna True si se agregó correctamente, False si no.
        """
        if 0 <= nota <= 100:
            self.datos[(actividad, carnet)] = nota
            self.filas.add(actividad)
            self.columnas.add(carnet)
            return True
        print(f"⚠️ Nota inválida para {carnet} en {actividad}: {nota}")
        return False

    def obtener_nota(self, actividad: str, carnet: str):
        """Devuelve la nota de un estudiante en una actividad específica."""
        return self.datos.get((actividad, carnet), None)

    def obtener_por_actividad(self, actividad: str):
        """Devuelve todas las notas de una actividad {carnet: nota}"""
        return {c: n for (a, c), n in self.datos.items() if a == actividad}

    def obtener_por_estudiante(self, carnet: str):
        """Devuelve todas las notas de un estudiante {actividad: nota}"""
        return {a: n for (a, c), n in self.datos.items() if c == carnet}

    def promedio_por_actividad(self, actividad: str) -> float:
        """Calcula el promedio de notas de una actividad."""
        notas = list(self.obtener_por_actividad(actividad).values())
        if not notas:
            return 0
        return sum(notas) / len(notas)

    def top_notas(self, actividad: str):
        """Devuelve lista ordenada de (carnet, nota) de mayor a menor."""
        notas = self.obtener_por_actividad(actividad)
        return sorted(notas.items(), key=lambda x: x[1], reverse=True)

    def obtener_todas_actividades(self):
        """Devuelve lista de todas las actividades."""
        return list(self.filas)

    def obtener_todos_estudiantes(self):
        """Devuelve lista de todos los carnets."""
        return list(self.columnas)

    def to_dict(self):
        """Convierte la matriz a diccionario para almacenamiento."""
        return {
            "datos": {f"{k[0]}|{k[1]}": v for k, v in self.datos.items()},
            "filas": list(self.filas),
            "columnas": list(self.columnas)
        }

    def from_dict(self, data):
        """Carga la matriz desde un diccionario."""
        self.filas = set(data.get("filas", []))
        self.columnas = set(data.get("columnas", []))
        self.datos = {}
        for key, value in data.get("datos", {}).items():
            partes = key.split("|")
            if len(partes) == 2:
                self.datos[(partes[0], partes[1])] = value