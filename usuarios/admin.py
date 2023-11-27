from django.contrib import admin
from .models import HistoriaClinica, Adenda, Usuario

admin.site.register(HistoriaClinica)
admin.site.register(Adenda)
admin.site.register(Usuario)