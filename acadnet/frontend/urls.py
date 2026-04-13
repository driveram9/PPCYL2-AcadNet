from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('student/', views.dashboard_student, name='student'),
    path('admin/', views.dashboard_admin, name='admin'),
    path('tutor/', views.dashboard_tutor, name='tutor'),
    #path('upload/', views.upload_view, name='upload'),
    #path('tabla/', views.tabla_view, name='tabla'),
]
