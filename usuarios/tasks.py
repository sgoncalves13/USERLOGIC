from .models import Usuario, UsuarioLectura
from django.core.exceptions import ObjectDoesNotExist
from django_orm_extensions.postgres.decorators import db_sync

@db_sync
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

@db_sync
def eliminar_usuario_lectura(documento):
    try:
        usuario_lectura = UsuarioLectura.objects.get(documento=documento)
        usuario_lectura.delete()
    except ObjectDoesNotExist:
        return None
