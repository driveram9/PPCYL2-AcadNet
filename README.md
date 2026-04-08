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

Recomendación de Archivos de proyecto:

Frontend (Django) — ~10–14 archivos
Archivos principales
- manage.py — script de gestión del proyecto Django.
- settings.py — configuración del proyecto (bases de datos, apps, rutas estáticas).
- urls.py — rutas globales del frontend que apuntan a vistas y a la API.
App(s) y vistas
- apps/academia/views.py — vistas que renderizan páginas (login, panel admin, tutor, estudiante).
- apps/academia/urls.py — rutas específicas de la app (endpoints de UI).
- apps/academia/forms.py — formularios para carga de XML, login y filtros de reportes.
- apps/academia/models.py (opcional) — modelos Django si decides persistir usuarios/roles localmente.
Templates y estáticos
- templates/login.html — formulario de inicio de sesión.
- templates/admin_dashboard.html — interfaz para administrador (carga XML, ver usuarios).
- templates/tutor_dashboard.html — carga horarios, subir notas, ver reportes.
- templates/estudiante_dashboard.html — consulta de notas.
- static/css/styles.css — estilos globales (puede dividirse en varios archivos).
- static/js/reports.js — scripts para renderizar gráficos (ChartJS/Plotly) y llamadas AJAX a la API.

Backend (Flask API) — ~6–10 archivos
Archivos principales
- app.py o run.py — punto de entrada del servicio Flask (registro de blueprints y configuración).
- config.py — configuración del servicio (puertos, rutas de archivos, credenciales de prueba).
- routes/auth.py — endpoint /login y lógica de autenticación.
- routes/uploads.py — endpoints para /uploadConfig, /uploadHorarios, /uploadNotas.
- routes/reports.py — endpoints para /getReportes, /getNotas, /getHorarios.
Módulos de lógica
- services/xml_processor.py — lectura, validación y transformación XML → JSON.
- services/matriz.py — implementación de la MatrizDispersa (POO) y operaciones CRUD sobre la matriz.
- services/reportes.py — generación de datos para reportes (promedios, top, agregados).
- schemas.py (opcional) — definiciones de payloads esperados (p. ej. con Marshmallow).

Módulos compartidos y utilidades — ~2–4 archivos
- common/models.py — clases de dominio reutilizables (Usuario, Curso, Tutor, Estudiante) usadas por frontend y backend si se comparte lógica.
- common/xml_templates/ — ejemplos de archivos de entrada y salida (ej.: config_entrada.xml, config_salida.xml) para pruebas.
- utils/validators.py — validaciones comunes (formato de hora, rango de nota, existencia de curso).

Recursos para reportes y gráficos — ~1–3 archivos
- reports/graphviz.dot (generado) — archivo DOT para Graphviz (resumen de notas).
- reports/plotly_config.js o reports/chart_config.py — plantillas para generar gráficos en frontend o backend.
- reports/export_pdf.py (opcional) — módulo que orquesta la conversión de gráficos a PDF (si se hace desde backend).

Archivos de configuración y soporte — ~4 archivos
- requirements.txt — dependencias Python (Flask, Django, lxml, plotly, graphviz, etc.).
- .gitignore — exclusiones de Git.
- README.md — instrucciones de instalación, endpoints y uso (obligatorio).
- Procfile / Dockerfile (opcional) — para despliegue o contenedorización.

Pruebas y documentación — ~2–4 archivos
- tests/test_matriz.py — pruebas unitarias para la MatrizDispersa.
- tests/test_xml_processor.py — pruebas para validación y transformación XML.
- docs/diagrama_clases.png — diagrama de clases requerido en la documentación.
- docs/ensayo.pdf — ensayo entre 2–5 páginas (subido al repo y al release).

Cómo se relacionan los módulos (breve)
- Frontend (Django): interfaz de usuario; envía archivos XML y solicitudes HTTP a la API Flask; consume JSON/XML de respuesta para mostrar tablas y gráficos.
- Backend (Flask): recibe y valida entradas; usa xml_processor para parsear; almacena notas en MatrizDispersa; genera datos para reportes y produce archivos XML de salida.
- MatrizDispersa: módulo POO independiente que actúa como la fuente de verdad para notas; expone métodos para insertar, consultar y exportar datos.
- Reportes: consumen la matriz para calcular promedios y rankings; producen datos JSON para frontend y archivos DOT/PDF para exportación.
- Archivos de configuración: requirements.txt, README.md y releases en GitHub documentan y permiten reproducir el entorno.
