from django.urls import path
from .views import AutenticacionAPI

urlpatterns = [
    path('autenticacion/', AutenticacionAPI.as_view()),
]