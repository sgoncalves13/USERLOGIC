from django.db import models

class HistoriaClinica(models.Model):
    id_hc = models.AutoField(primary_key=True)
    diagnosticos = models.CharField(max_length=500)
    tratamientos = models.CharField(max_length=500)
    notas = models.CharField(max_length=500)

class Usuario(models.Model):
    documento = models.CharField(max_length=15, primary_key=True)
    clave = models.CharField(max_length=30)
    tipo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=30)
    edad = models.CharField(max_length=30)
    telefono = models.CharField(max_length=30)
    sexo = models.CharField(max_length=30)
    foto = models.CharField(max_length=255)
    historia_clinica = models.OneToOneField(HistoriaClinica, on_delete=models.CASCADE, related_name='usuario', null=True, blank=True)
    medico = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='pacientes')

class Adenda(models.Model):
    id_adenda = models.AutoField(primary_key=True)
    fecha = models.CharField(max_length=40)
    tipo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=500)
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE, related_name='adendas')


