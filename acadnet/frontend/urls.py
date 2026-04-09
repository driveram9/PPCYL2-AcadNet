from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboardStudent/', views.dashboard_view, name='dashboardStudent'),
    path('upload/', views.upload_view, name='upload'),
    path('tabla/', views.tabla_view, name='tabla'),
]
