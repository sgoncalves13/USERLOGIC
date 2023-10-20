from django.urls import path
from .views import AutenticacionAPI, UsuarioAPI


urlpatterns = [
    path('autenticacion/', AutenticacionAPI.as_view()),
    path('usuario/', UsuarioAPI.as_view()),
]