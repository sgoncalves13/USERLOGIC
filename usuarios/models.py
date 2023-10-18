from django.db import models

class Usuario(models.Model):
    documento = models.CharField(max_length=15)
    clave = models.CharField(max_length=30)
    tipo = models.CharField(max_length=30)
   

class HistoriaClinica(models.Model):
    id_hc = models.IntegerField(primary_key=True)
    diagnosticos =models.CharField(max_length=None)
    tratamientos = models.CharField(max_length=None)
    notas = models.CharField(max_length=None)
    idusuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='historia_clinica')


class Adenda(models.Models):
    id_adenda = models.IntegerField(primary_key=True)
    autor = models.CharField(max_length=40)
    tipo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=None)
    idhistoriaclinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE, related_name='adendas')

