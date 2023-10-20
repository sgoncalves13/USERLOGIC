from django.urls import path
from .views import agregarAdendaAPI, UsuarioAPI

urlpatterns = [
    path('agregarAdenda/', agregarAdendaAPI.as_view()),
    path('usuario/', UsuarioAPI.as_view()),
]