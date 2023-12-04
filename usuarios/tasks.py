from .models import Usuario, UsuarioLectura
from django.core.exceptions import ObjectDoesNotExist
from asgiref.sync import sync_to_async

@sync_to_async
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

@sync_to_async
def eliminar_usuario_lectura(documento):
    try:
        usuario_lectura = UsuarioLectura.objects.get(documento=documento)
        usuario_lectura.delete()
    except ObjectDoesNotExist:
        return None
