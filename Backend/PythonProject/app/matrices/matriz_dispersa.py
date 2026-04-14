# Matriz Dispersa para almacenar notas de estudiantes
# Representación: Diccionario de diccionarios

class MatrizDispersa:
    """
    Matriz dispersa para almacenar notas de estudiantes.
    - Filas: Actividades
    - Columnas: Carnet de estudiantes
    - Valor: Nota
    """

    def __init__(self):
        self.datos = {}  # Diccionario principal
        self.filas = set()  # Conjunto de nombres de actividades
        self.columnas = set()  # Conjunto de carnets

    def agregar(self, actividad, carnet, nota):
        """Agrega una nota a la matriz"""
        # Validar nota (0-100)
        if nota < 0 or nota > 100:
            print(f"⚠️ Nota {nota} fuera de rango (0-100). No se agregó.")
            return False

        # Crear estructura si no existe
        if actividad not in self.datos:
            self.datos[actividad] = {}

        # Guardar la nota
        self.datos[actividad][carnet] = nota
        self.filas.add(actividad)
        self.columnas.add(carnet)
        return True

    def obtener(self, actividad, carnet):
        """Obtiene una nota específica"""
        return self.datos.get(actividad, {}).get(carnet, None)

    def obtener_fila(self, actividad):
        """Obtiene todas las notas de una actividad (fila completa)"""
        return self.datos.get(actividad, {})

    def obtener_columna(self, carnet):
        """Obtiene todas las notas de un estudiante (columna completa)"""
        resultado = {}
        for actividad, estudiantes in self.datos.items():
            if carnet in estudiantes:
                resultado[actividad] = estudiantes[carnet]
        return resultado

    # ============================================
    # NUEVO MÉTODO: obtener_por_estudiante
    # ============================================
    def obtener_por_estudiante(self, carnet):
        """
        Obtiene todas las notas de un estudiante.
        Retorna un diccionario {actividad: nota}
        """
        return self.obtener_columna(carnet)

    def promedio_por_actividad(self, actividad):
        """Calcula el promedio de notas para una actividad"""
        fila = self.obtener_fila(actividad)
        if not fila:
            return 0
        notas = list(fila.values())
        return sum(notas) / len(notas)

    def top_notas(self, actividad):
        """Obtiene lista ordenada de (carnet, nota) de mayor a menor"""
        fila = self.obtener_fila(actividad)
        if not fila:
            return []
        # Ordenar por nota (mayor a menor)
        ordenado = sorted(fila.items(), key=lambda x: x[1], reverse=True)
        return ordenado

    def obtener_todas_actividades(self):
        """Devuelve lista de todas las actividades"""
        return list(self.filas)

    def obtener_todos_estudiantes(self):
        """Devuelve lista de todos los carnets"""
        return list(self.columnas)

    def to_dict(self):
        """Convierte la matriz a diccionario para almacenamiento"""
        return {
            "datos": self.datos,
            "filas": list(self.filas),
            "columnas": list(self.columnas)
        }

    def from_dict(self, data):
        """Carga la matriz desde un diccionario"""
        self.datos = data.get("datos", {})
        self.filas = set(data.get("filas", []))
        self.columnas = set(data.get("columnas", []))