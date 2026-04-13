from django.urls import path
from . import views

urlpatterns = [
    # Vistas principales
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('tutor/', views.tutor_dashboard, name='tutor_dashboard'),
    path('estudiante/', views.estudiante_dashboard, name='estudiante_dashboard'),

    path('api/tutor/horarios', views.api_tutor_horarios, name='api_tutor_horarios'),
    path('api/tutor/limpiar-horarios', views.api_tutor_limpiar_horarios, name='api_tutor_limpiar_horarios'),
    path('api/tutor/cargar-horarios', views.api_tutor_cargar_horarios, name='api_tutor_cargar_horarios'),
    path('api/tutor/notas', views.api_tutor_notas, name='api_tutor_notas'),
    path('api/tutor/reportes', views.api_tutor_reportes, name='api_tutor_reportes'),

    path('api/estudiante/cursos/<str:carnet>', views.api_estudiante_cursos, name='api_estudiante_cursos'),
    path('api/estudiante/tareas/<str:carnet>', views.api_estudiante_tareas, name='api_estudiante_tareas'),
    path('api/estudiante/notas/<str:carnet>', views.api_estudiante_notas, name='api_estudiante_notas'),
    path('api/estudiante/anuncios', views.api_estudiante_anuncios, name='api_estudiante_anuncios'),
    path('api/estudiante/horarios', views.api_estudiante_horarios, name='api_estudiante_horarios'),
]
