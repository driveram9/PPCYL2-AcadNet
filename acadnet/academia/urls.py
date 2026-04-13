from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('student/', views.estudiante_dashboard, name='student'),
    path('admin/', views.admin_dashboard, name='admin'),
    path('tutor/', views.tutor_dashboard, name='tutor'),
    #path('upload/', views.upload_view, name='upload'),
    #path('tabla/', views.tabla_view, name='tabla'),
]
