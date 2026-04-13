from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('student/', views.estudiante_dashboard, name='student'),
    path('dashboard-admin/', views.admin_dashboard, name='admin-dashboard'),
    path('tutor/', views.tutor_dashboard, name='tutor'),
]
