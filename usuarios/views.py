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

def agregar_usuario(documento, clave, tipo, nombre, edad, telefono, sexo, foto):
    nuevo_usuario = Usuario(
        documento=documento,
        clave=clave,
        tipo=tipo,
        nombre=nombre,
        edad=edad,
        telefono=telefono,
        sexo=sexo,
        foto=foto
    )
    nuevo_usuario.save()
    print(f"> Usuario agregado con éxito: documento={documento}, clave={clave}, tipo={tipo}, nombre={nombre}, edad={edad}, telefono={telefono}, sexo={sexo}, foto={foto}")



 # Asegúrate de importar el modelo de Usuario desde tu aplicación
def obtener_usuario_por_documento(documento):
    try:
        usuario = Usuario.objects.get(documento=documento)
        return usuario
    except Usuario.DoesNotExist:
        return None


def agregar_paciente_a_medico(documento_medico, documento_paciente):
    try:
        # Buscar al médico y al paciente por sus documentos
        medico = Usuario.objects.get(documento=documento_medico)
        paciente = Usuario.objects.get(documento=documento_paciente)

        paciente.medico.add(medico)

        return True  # Devuelve True si la operación fue exitosa
    except Usuario.DoesNotExist:
        # El médico o el paciente no existen en la base de datos
        return False  # Devuelve False si hay un error



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

class UsuarioAPI(APIView):

    def consultar_usuario(self, request):
        # Obtener el documento de usuario desde la solicitud
        documento = request.data.get('documento')

        # Realizar una consulta a la base de datos para obtener el usuario
        try:
            usuario = Usuario.objects.get(documento=documento)
        except Usuario.DoesNotExist:
            # Manejar el caso en el que el usuario no existe
            respuesta_post = {'error': 'Usuario no encontrado'}
            return Response(respuesta_post, status=status.HTTP_404_NOT_FOUND)

        # Crear un diccionario con los atributos del usuario
        usuario_dict = {
            'documento': usuario.documento,
            'clave': usuario.clave,
            'tipo': usuario.tipo,
            'nombre': usuario.nombre,
            'edad': usuario.edad,
            'telefono': usuario.telefono,
            'sexo': usuario.sexo,
            'foto': usuario.foto  # Añade más atributos según sea necesario
        }

        # Responder con el diccionario en formato JSON
        respuesta_post = {'usuario': usuario_dict}
        return Response(respuesta_post, status=status.HTTP_200_OK)



