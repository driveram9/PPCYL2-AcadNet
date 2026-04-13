from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('panel-admin/', views.admin_dashboard, name='admin_dashboard'),  # ← Cambiar nombre
    path('tutor/', views.tutor_dashboard, name='tutor_dashboard'),
    path('estudiante/', views.estudiante_dashboard, name='estudiante_dashboard'),
    path('logout/', views.logout_view, name='logout'),

]