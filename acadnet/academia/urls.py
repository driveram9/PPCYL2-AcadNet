from django.urls import path
from . import views

urlpatterns = [
    # Vistas principales
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboards
    path('panel-admin/', views.admin_dashboard, name='admin_dashboard'),
    path('tutor/', views.tutor_dashboard, name='tutor_dashboard'),
    path('estudiante/', views.estudiante_dashboard, name='estudiante_dashboard'),

    # APIs del administrador
    path('api/admin/cursos', views.api_admin_cursos, name='api_admin_cursos'),
    path('api/admin/tutores', views.api_admin_tutores, name='api_admin_tutores'),
    path('api/admin/estudiantes', views.api_admin_estudiantes, name='api_admin_estudiantes'),
    path('api/admin/upload', views.api_admin_upload, name='api_admin_upload'),
    path('api/admin/procesar', views.api_admin_procesar, name='api_admin_procesar'),
    path('api/admin/xml', views.api_admin_xml, name='api_admin_xml'),
    path('api/admin/limpiar', views.api_admin_limpiar, name='api_admin_limpiar'),

    # APIs del tutor
    path('api/tutor/horarios', views.api_tutor_horarios, name='api_tutor_horarios'),
    path('api/tutor/limpiar-horarios', views.api_tutor_limpiar_horarios, name='api_tutor_limpiar_horarios'),
    path('api/tutor/cargar-horarios', views.api_tutor_cargar_horarios, name='api_tutor_cargar_horarios'),
    path('api/tutor/notas', views.api_tutor_notas, name='api_tutor_notas'),
    path('api/tutor/reportes', views.api_tutor_reportes, name='api_tutor_reportes'),

    # APIs del estudiante
    path('api/estudiante/notas', views.api_estudiante_notas, name='api_estudiante_notas'),
    path('api/estudiante/cursos', views.api_estudiante_cursos, name='api_estudiante_cursos'),
    path('api/estudiante/tareas', views.api_estudiante_tareas, name='api_estudiante_tareas'),
    path('api/estudiante/anuncios', views.api_estudiante_anuncios, name='api_estudiante_anuncios'),
    path('api/estudiante/horarios', views.api_estudiante_horarios, name='api_estudiante_horarios'),
]