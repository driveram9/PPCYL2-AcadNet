from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('frontend-django.urls')),
    path('admin/', admin.site.urls),
]