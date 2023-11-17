from django.urls import path
from .views import usuarioAPI, historiaClinicaAPI, agregarAdendaAPI

urlpatterns = [
    path("usuario/", usuarioAPI.as_view()),
    path("historia_clinica/", historiaClinicaAPI.as_view()),
    path("agregar_adenda/", agregarAdendaAPI.as_view())
]