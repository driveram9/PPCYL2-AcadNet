class MatrizDispersa:
    def __init__(self):
        self.data = {}

    def insertar(self, fila, columna, valor):
        self.data[(fila, columna)] = valor

    def obtener(self, fila, columna):
        return self.data.get((fila, columna))

    def eliminar(self, fila, columna):
        if (fila, columna) in self.data:
            del self.data[(fila, columna)]
