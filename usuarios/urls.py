from django.urls import path
from .views import agregarAdendaAPI, UsuarioAPI, ListaPacientesAPI

urlpatterns = [
    path('agregarAdenda/', agregarAdendaAPI.as_view()),
    path('usuario/', UsuarioAPI.as_view()),
    path('medico/<str:documento_medico>/pacientes/', ListaPacientesAPI.as_view(), name='listar_pacientes_api'),
]