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
        foto=foto,
    )
    nuevo_usuario.save()
    print(f"> Usuario agregado con éxito: documento={documento}, clave={clave}, tipo={tipo}, nombre={nombre}, edad={edad}, telefono={telefono}, sexo={sexo}, foto={foto}")



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

        print("Paciente agregado con exito")  # Devuelve True si la operación fue exitosa
    except Usuario.DoesNotExist:
        # El médico o el paciente no existen en la base de datos
        print("Paciente NO se agrego con exito")  # Devuelve True si la operación fue exitosa

def eliminar_usuario_por_documento(documento):
    try:
        # Buscar el usuario por su documento
        usuario = Usuario.objects.get(documento=documento)
        # Eliminar el usuario
        usuario.delete()
        return "Usuario eliminado con éxito."
    except Usuario.DoesNotExist:
        return "Usuario no encontrado."
    
#agregar_usuario('1092524481', '123', 'profesionalSalud','Jefferson Hernandez','20', '3023464345', 'Masculino', 'https://i.ibb.co/ZGqCFwb/carlitos.png')
#agregar_usuario('1234567890', '123', 'profesionalSalud', 'Carlos Muñoz', '20', '3164614926', 'Masculino', 'https://i.ibb.co/ZGqCFwb/carlitos.png')
eliminar_usuario_por_documento('0987654321')
agregar_usuario('0987654321', '123', 'paciente', 'Harold Samuel Hernandez', '25', '323232323232', 'Masculino', 'https://i.ibb.co/ZgNP89g/image-2023-10-20-103230643.png')
#agregar_usuario('3232323232', '123', 'paciente', 'Luis Andres Garcia', '45', '31202034044', 'Masculino', 'https://i.ibb.co/BsMgQnH/image-2023-10-20-102702811.png')
#agregar_usuario('2323232232', '123', 'director', 'Claudia Patricia Suarez', '50', '323232332', 'Femenino', 'https://i.ibb.co/3ydfwNR/image-2023-10-20-102845276.png')
agregar_paciente_a_medico('1234567890', '0987654321')

def agregar_adenda_a_usuario(documento_paciente, documento_profesional, fecha, tipo, descripcion):

    try:
        # Buscar el usuario por documento
        usuario = Usuario.objects.get(documento=documento_paciente)

        # Verificar si el usuario tiene al profesional de salud
        profesional = Usuario.objects.get(documento=documento_profesional)
        
        if not usuario.medico.filter(documento=documento_profesional).exists():
            # Si el paciente no tiene al profesional de salud, devuelve None
            return None

        # Verificar si el usuario tiene una historia clínica
        if not usuario.historia_clinica:
            nueva_historia_clinica = HistoriaClinica(
            diagnosticos="Ninguno",
            tratamientos="Ninguno",
            notas="Ninguno"
            )
            nueva_historia_clinica.save()
            usuario.historia_clinica = nueva_historia_clinica
            usuario.save()

        # Ahora, puedes crear la adenda y asociarla a la historia clínica
        adenda = Adenda(fecha=fecha, tipo=tipo, descripcion=descripcion, historia_clinica=usuario.historia_clinica)
        adenda.save()

        historia_clinica_data = {
            'id_hc': usuario.historia_clinica.id_hc,
            'diagnosticos': usuario.historia_clinica.diagnosticos,
            'tratamientos': usuario.historia_clinica.tratamientos,
            'notas': usuario.historia_clinica.notas
        }

        adenda_data = {
            'id': adenda.id_adenda,
            'fecha': adenda.fecha,
            'tipo': adenda.tipo,
            'descripcion': adenda.descripcion,
            'historia_clinica': historia_clinica_data
        }

        return adenda_data

    except Usuario.DoesNotExist:
        return None

class UsuarioAPI(APIView):

    def post(self, request):
        # Obtener el documento de usuario desde la solicitud
        documento = request.data.get('documento')

        # Realizar una consulta a la base de datos para obtener el usuario
        try:
            usuario = Usuario.objects.get(documento=documento)
        except Usuario.DoesNotExist:
            # Manejar el caso en el que el usuario no existe
            respuesta_post = {'error': 'Usuario no encontrado'}
            return Response(respuesta_post, status=status.HTTP_404_NOT_FOUND)

        # Si el usuario tiene una historia clínica, obtener las adendas
        adendas_list = []
        if usuario.historia_clinica:
            adendas = Adenda.objects.filter(historia_clinica=usuario.historia_clinica)
            adendas_list = [
                {
                    "id_adenda": adenda.id_adenda,
                    "fecha": adenda.fecha,
                    "tipo": adenda.tipo,
                    "descripcion": adenda.descripcion
                } for adenda in adendas
            ]

        dict_historiaclinica = {}
        if usuario.historia_clinica:
            hc = usuario.historia_clinica
            dict_historiaclinica["id"] = hc.id_hc
            dict_historiaclinica["diagnosticos"] = hc.diagnosticos
            dict_historiaclinica["tratamientos"] = hc.tratamientos
            dict_historiaclinica["notas"] = hc.notas


        # Crear un diccionario con los atributos del usuario
        usuario_dict = {
            'documento': usuario.documento,
            'clave': usuario.clave,
            'tipo': usuario.tipo,
            'nombre': usuario.nombre,
            'edad': usuario.edad,
            'telefono': usuario.telefono,
            'sexo': usuario.sexo,
            'foto': usuario.foto, 
            'historia_clinica' : dict_historiaclinica,
            'adendas': adendas_list  # Añadir las adendas aquí
        }

        # Responder con el diccionario en formato JSON
        respuesta_post = usuario_dict
        return Response(respuesta_post, status=status.HTTP_200_OK)
    
class agregarAdendaAPI(APIView):

    def post(self, request):

        documento_paciente = request.data.get('documento_paciente')
        documento_profesional = request.data.get('documento_profesional')
        fecha = request.data.get('fecha')
        tipo = request.data.get('tipo')
        descripcion = request.data.get('descripcion')

        respuesta = agregar_adenda_a_usuario(documento_paciente, documento_profesional, fecha, tipo, descripcion)

        respuesta_post = {'adenda': respuesta}

        return Response(respuesta_post, status=status.HTTP_200_OK)
    
class ListaPacientesAPI(APIView):

    def post(self, request, documento_medico):
        try:
            # Obtener el objeto médico a partir del documento
            medico = Usuario.objects.get(documento=documento_medico)

            # Obtener todos los pacientes asociados a este médico
            pacientes = medico.pacientes.all()

            # Crear una lista para almacenar la información de los pacientes
            lista_pacientes = []
            for paciente in pacientes:
                lista_pacientes.append({
                    'documento': paciente.documento,
                    'nombre': paciente.nombre
                })

            # Retornar la lista de pacientes
            return Response(lista_pacientes, status=status.HTTP_200_OK)

        except Usuario.DoesNotExist:
            # Manejar el caso en que el médico no exista
            return Response({'error': 'Médico no encontrado'}, status=status.HTTP_404_NOT_FOUND)



