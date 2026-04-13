class MatrizDispersa:
    """Matriz dispersa para almacenar notas de estudiantes"""

    def __init__(self):
        self.datos = {}
        self.filas = set()
        self.columnas = set()

    def agregar(self, actividad: str, carnet: str, nota: float) -> bool:
        if 0 <= nota <= 100:
            self.datos[(actividad, carnet)] = nota
            self.filas.add(actividad)
            self.columnas.add(carnet)
            return True
        return False

    def obtener_nota(self, actividad: str, carnet: str):
        return self.datos.get((actividad, carnet), None)

    def obtener_por_actividad(self, actividad: str):
        return {c: n for (a, c), n in self.datos.items() if a == actividad}

    def obtener_por_estudiante(self, carnet: str):
        return {a: n for (a, c), n in self.datos.items() if c == carnet}

    def promedio_por_actividad(self, actividad: str) -> float:
        notas = list(self.obtener_por_actividad(actividad).values())
        return sum(notas) / len(notas) if notas else 0

    def top_notas(self, actividad: str):
        notas = self.obtener_por_actividad(actividad)
        return sorted(notas.items(), key=lambda x: x[1], reverse=True)

    def obtener_todas_actividades(self):
        return list(self.filas)

    def obtener_todos_estudiantes(self):
        return list(self.columnas)

    def to_dict(self):
        return {
            "datos": {f"{k[0]}|{k[1]}": v for k, v in self.datos.items()},
            "filas": list(self.filas),
            "columnas": list(self.columnas)
        }

    def from_dict(self, data):
        self.filas = set(data.get("filas", []))
        self.columnas = set(data.get("columnas", []))
        self.datos = {}
        for key, value in data.get("datos", {}).items():
            partes = key.split("|")
            if len(partes) == 2:
                self.datos[(partes[0], partes[1])] = value