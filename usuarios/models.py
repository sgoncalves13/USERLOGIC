from django.db import models

class HistoriaClinica(models.Model):
    diagnosticos = models.CharField(max_length=500)
    tratamientos = models.CharField(max_length=500)
    notas = models.CharField(max_length=500)

class Adenda(models.Model):
    fecha = models.CharField(max_length=40)
    tipo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=500)
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE, related_name='adendas')

class Usuario(models.Model):
    documento = models.CharField(max_length=15, primary_key=True)
    clave = models.CharField(max_length=30, default='123')
    tipo = models.CharField(max_length=30, default='default')
    foto = models.CharField(max_length=255, default='default')
    nombre = models.CharField(max_length=30, default='default')
    edad = models.CharField(max_length=30, default='default')
    telefono = models.CharField(max_length=30, default='default')
    sexo = models.CharField(max_length=30, default='default')
    historia_clinica = models.OneToOneField(HistoriaClinica, on_delete=models.CASCADE, related_name='usuario', null=True, blank=True)
    medico = models.OneToOneField('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='paciente', limit_choices_to={'tipo': 'paciente'})