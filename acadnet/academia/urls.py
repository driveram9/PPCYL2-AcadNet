from django.urls import path
from . import views

urlpatterns = [
    # Vistas principales
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboards
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('tutor/', views.tutor_dashboard, name='tutor_dashboard'),
    path('estudiante/', views.estudiante_dashboard, name='estudiante_dashboard'),

    # APIs para el tutor
    path('api/tutor/horarios', views.api_tutor_horarios, name='api_tutor_horarios'),
    path('api/tutor/cargar-horarios', views.api_tutor_cargar_horarios, name='api_tutor_cargar_horarios'),
    path('api/tutor/notas', views.api_tutor_notas, name='api_tutor_notas'),
    path('api/tutor/reportes', views.api_tutor_reportes, name='api_tutor_reportes'),
]