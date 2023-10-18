from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Usuario

def verificar_usuario(documento, clave):
    try:
        usuario = Usuario.objects.get(documento=documento, clave=clave)
        respuesta = "valido"
        tipo = usuario.tipo
    except Usuario.DoesNotExist:
        respuesta = "invalido"
        tipo = ""

    return respuesta, tipo

def agregar_usuario(documento, clave, tipo):
    nuevo_usuario = Usuario(documento=documento, clave=clave, tipo=tipo)
    nuevo_usuario.save()
    print("> documento: "+ documento + ", clave: " + clave + ", tipo: " + tipo + ". Agregado con exito")

class AutenticacionAPI(APIView):

    def post(self, request):

        documento = request.data.get('documento')
        clave = request.data.get('clave')

        respuesta, tipo = verificar_usuario(documento, clave)

        respuesta_post = {'respuesta': respuesta, 'tipo': tipo}

        return Response(respuesta_post, status=status.HTTP_200_OK)



