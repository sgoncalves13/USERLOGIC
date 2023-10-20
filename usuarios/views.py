from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Usuario, Adenda, HistoriaClinica

def verificar_usuario(documento, clave):
    try:
        usuario = Usuario.objects.get(documento=documento, clave=clave)
        respuesta = "valido"
        tipo = usuario.tipo
    except Usuario.DoesNotExist:
        respuesta = "invalido"
        tipo = ""

    return respuesta, tipo
 # Asegúrate de importar el modelo de Usuario desde tu aplicación
def obtener_usuario_por_documento(documento):
    try:
        usuario = Usuario.objects.get(documento=documento)
        return usuario
    except Usuario.DoesNotExist:
        return None

def agregar_adenda_a_usuario(documento, fecha, tipo, descripcion):
    try:
        # Buscar el usuario por documento
        usuario = Usuario.objects.get(documento=documento)

        # Verificar si el usuario tiene una historia clínica
        if not usuario.historia_clinica:
            # Si el usuario no tiene una historia clínica, crea una nueva y asígnala al usuario
            nueva_historia_clinica = HistoriaClinica()
            nueva_historia_clinica.save()
            usuario.historia_clinica = nueva_historia_clinica
            usuario.save()

        # Ahora, puedes crear la adenda y asociarla a la historia clínica
        adenda = Adenda(fecha=fecha, tipo=tipo, descripcion=descripcion, historia_clinica=usuario.historia_clinica)
        adenda.save()
        return adenda
    except Usuario.DoesNotExist:
        # El usuario no existe en la base de datos
        return None




class AutenticacionAPI(APIView):

    def post(self, request):

        documento = request.data.get('documento')
        clave = request.data.get('clave')

        respuesta, tipo = verificar_usuario(documento, clave)

        respuesta_post = {'respuesta': respuesta, 'tipo': tipo}

        return Response(respuesta_post, status=status.HTTP_200_OK)



