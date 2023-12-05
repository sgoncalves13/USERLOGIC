from django.urls import path
from django.contrib import admin
from .views import usuarioAPI, historiaClinicaAPI, agregarAdendaAPI, usuariosAPI

urlpatterns = [
    path('admin/', admin.site.urls),
    path("usuario/", usuarioAPI.as_view()),
    path("usuarios/", usuariosAPI.as_view()),
    path("historia_clinica/", historiaClinicaAPI.as_view()),
    path("agregar_adenda/", agregarAdendaAPI.as_view())
]