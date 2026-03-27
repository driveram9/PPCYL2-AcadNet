Les Comparto el enlace de Diseño de Software compañeros
https://canva.link/6uxerasxktbrisx

Planteamiento de Clases y Variables:

1. Usuario
- Variables:
  - id → identificador único.
  - usuario → nombre de usuario.
  - contrasenia → contraseña.
  - rol → tipo de usuario (admin, tutor, estudiante).

2. Administrador (hereda de Usuario)
- Variables:
  - archivos_cargados → lista de XML procesados.
  - usuarios_configurados → lista de usuarios cargados desde XML.
  - reportes_generados → historial de reportes.

3. Tutor (hereda de Usuario)
- Variables:
  - registro_personal → identificador único del tutor.
  - cursos_asignados → lista de cursos.
  - horarios → horarios de tutoría (día, hora inicio, hora fin).
  - notas → matriz dispersa con notas de estudiantes.

4. Estudiante (hereda de Usuario)
- Variables:
  - carnet → identificador único del estudiante.
  - cursos_inscritos → lista de cursos.
  - notas → notas por curso (consultadas desde la matriz dispersa).

5. Curso
- Variables:
  - codigo → código del curso.
  - nombre → nombre del curso.
  - tutor_asignado → ID del tutor.
  - estudiantes → lista de carnets inscritos.

6. MatrizDispersa
- Variables:
  - filas → actividades (ej. Tarea1, Examen1).
  - columnas → carnets de estudiantes.
  - valores → notas (0–100).
  - Métodos: insertar nota, actualizar, generar reporte.

7. ArchivoXML
- Variables:
  - ruta → ubicación del archivo.
  - contenido → datos cargados.
  - Métodos: leer, validar, transformar a JSON, generar salida.
