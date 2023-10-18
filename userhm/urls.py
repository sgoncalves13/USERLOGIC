from django.urls import include, path
from . import views

urlpatterns = [
    path('', include('usuarios.urls')),
    path('health-check/', views.healthCheck)
]
