from django.urls import path
from .views import agregarAdendaAPI, usuarioAPI, historiaClinicaAPI

urlpatterns = [
    path("agregar_adenda/", agregarAdendaAPI.as_view()),
    path("usuario/", usuarioAPI.as_view()),
    path("historia_clinica/", historiaClinicaAPI.as_view())
]