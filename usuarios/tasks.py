from celery import shared_task
from .models import Usuario, UsuarioLectura

@shared_task
def agregar_usuario_lectura(documento):
    usuario = Usuario.objects.get(documento=documento)
    usuario_lectura = UsuarioLectura(
       documento = usuario.documento,
       foto = usuario.foto,
       nombre = usuario.nombre,
       edad = usuario.edad,
       telefono = usuario.telefono,
       sexo = usuario.sexo
    )
    usuario_lectura.save()

def eliminar_usuario_lectura(documento):
    usuario_lectura = UsuarioLectura.objects.get(documento=documento)
    if usuario_lectura:
        usuario_lectura.delete()
