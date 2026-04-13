from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    #path('student/', views.estudiante_dashboard, name='student'),
    #path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    #path('tutor/', views.tutor_dashboard, name='tutor'),
]
