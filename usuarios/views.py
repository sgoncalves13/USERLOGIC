import json
from django.core.exceptions import ObjectDoesNotExist
import jwt
from django.conf import settings
import hashlib
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Usuario, Adenda, HistoriaClinica
from cryptography.fernet import Fernet

cipher_suite = Fernet('SebastianRamirezLeMeteMuyDuro')

def cifrar_dato(dato):
    return cipher_suite.encrypt(dato.encode())

def obtener_usuario_por_documento(documento):
    usuario = Usuario.objects.get(documento=documento)
    return usuario
    
def obtener_historia_por_documento(documento_paciente, documento_profesional):
    usuario = Usuario.objects.get(documento=documento_paciente)

    #if documento_profesional is not None:
    #    if usuario.medico is None or usuario.medico.documento != documento_profesional:
    #        return Response({"mensaje": "true"}, status=status.HTTP_200_OK)
            
    return usuario.historia_clinica
    
def agregar_usuario(documento, clave, tipo, nombre, edad, telefono, sexo, foto):

    documento_cifrado = cifrar_dato(documento)
    clave_cifrado = cifrar_dato(clave)
    tipo_cifrado = cifrar_dato(tipo)
    nombre_cifrado = cifrar_dato(nombre)
    edad_cifrado = cifrar_dato(edad)
    telefono_cifrado = cifrar_dato(telefono)
    sexo_cifrado = cifrar_dato(sexo)
    foto_cifrado = cifrar_dato(foto)

    usuario = Usuario(
        documento=documento_cifrado,
        clave=clave_cifrado,
        tipo=tipo_cifrado,
        foto=foto_cifrado,
        nombre=nombre_cifrado,
        edad=edad_cifrado,
        telefono=telefono_cifrado,
        sexo=sexo_cifrado,
    )

    usuario.save()
    return usuario
    
def agregar_profesional_a_usuario(documento_profesional, documento_paciente):
    profesional = Usuario.objects.get(documento=documento_profesional, tipo='profesionalSalud')
    usuario = Usuario.objects.get(documento=documento_paciente)
    if not usuario.medico:
        usuario.medico = profesional
        usuario.save()
        return usuario

def agregar_adenda_a_usuario(documento_paciente, documento_profesional, fecha, tipo, descripcion):

    try:
        usuario = Usuario.objects.get(documento=documento_paciente)
        if usuario.medico is None or usuario.medico.documento != documento_profesional:
            return "true"
        if not usuario.historia_clinica:
            nueva_historia_clinica = HistoriaClinica(
                diagnosticos="No se ha presentado ningún diagnostico",
                tratamientos="No se han presentados tratamientos",
                notas="No hay notas sobre el paciente"
            )
            nueva_historia_clinica.save()
            usuario.historia_clinica = nueva_historia_clinica
            usuario.save()
        adenda = Adenda(fecha=fecha, tipo=tipo, descripcion=descripcion, historia_clinica=usuario.historia_clinica)
        adenda.save()
        return None

    except Usuario.DoesNotExist:
        return "false"

def eliminar_usuario_por_documento(documento):
    try:
        usuario = Usuario.objects.get(documento=documento)
        usuario.delete()
    except ObjectDoesNotExist:
        return None

class usuarioAPI(APIView):

    def post(self, request):

        documento = request.data.get("documento")

        usuario = obtener_usuario_por_documento(documento)

        dict_usuario = {
            "documento": usuario.documento,
            "foto": usuario.foto,
            "nombre": usuario.nombre,
            "edad": usuario.edad,
            "telefono": usuario.telefono,
            "sexo": usuario.sexo,
        }

        return Response({"usuario":dict_usuario}, status=status.HTTP_200_OK)
            
class historiaClinicaAPI(APIView):

    def post(self, request):

        documento_paciente = request.data.get("documento_paciente")
        documento_profesional = request.data.get("documento_profesional")
        
        historia = obtener_historia_por_documento(documento_paciente, documento_profesional)

        if historia:
            dict_historia = {}
            dict_historia["diagnosticos"] = historia.diagnosticos
            dict_historia["tratamientos"] = historia.tratamientos
            dict_historia["notas"] = historia.notas
            adendas = Adenda.objects.filter(historia_clinica=historia)
            adendas_list = [
                {
                    "fecha": adenda.fecha,
                    "tipo": adenda.tipo,
                    "descripcion": adenda.descripcion
                } for adenda in adendas
            ]
            dict_historia["adendas"] = adendas_list

            return Response({"historia_clinica":dict_historia}, status=status.HTTP_200_OK)

        return Response({}, status=status.HTTP_200_OK)
    
class agregarAdendaAPI(APIView):

    def post(self, request):

        documento_paciente = request.data.get("documento_paciente")
        documento_profesional = request.data.get("documento_profesional")
        fecha = request.data.get("fecha")
        tipo = request.data.get("tipo")
        descripcion = request.data.get("descripcion")

        informacion_adenda = {"documento_paciente": documento_paciente, "documento_profesional": documento_profesional, "fecha": fecha, "tipo": tipo, "descripcion": descripcion}
        print("")
        print(">Información_Recibida:", informacion_adenda)
        informacion_firma = json.dumps(informacion_adenda, sort_keys=True)

        firma_calculada = hashlib.sha256(informacion_firma.encode()).hexdigest()

        print(">Hash_Calculado:", firma_calculada)

        firma_mensaje_cifrada = request.data.get("firma_jwt")

        if firma_mensaje_cifrada is None:
            return Response({"mensaje":"La petición no es valida porque no cuenta con el hash de la información cifrado por el servidor"}, status=status.HTTP_200_OK)

        print(">Hash_Cifrado_Recibido:", firma_mensaje_cifrada)
        decoded_firma = jwt.decode(firma_mensaje_cifrada, settings.SECRET_KEY, algorithms=["HS256"])

        print(">Hash_Decodificado_Recibido:", decoded_firma.get("firma"))
        print(">Son iguales?:", firma_calculada == decoded_firma.get("firma"))
        print("")

        if firma_calculada == decoded_firma.get("firma"):
            mensaje = agregar_adenda_a_usuario(documento_paciente, documento_profesional, fecha, tipo, descripcion)
        else:
            mensaje = "manipulado"

        return Response({"mensaje":mensaje}, status=status.HTTP_200_OK)
    

# INICIALIZACIÓN DE LA BASE DE DATOS

Usuario.objects.all().delete()


eliminar_usuario_por_documento("1234567890")
eliminar_usuario_por_documento("0987654321")
agregar_usuario("1234567890", "123", "profesionalSalud", "Carlos Muñoz", "20", "3164614926", "Masculino", "https://i.ibb.co/ZGqCFwb/carlitos.png")
agregar_usuario("0987654321", "123", "paciente", "Harold Samuel Hernandez", "25", "3026444020", "Masculino", "https://i.ibb.co/ZgNP89g/image-2023-10-20-103230643.png")
agregar_profesional_a_usuario('1234567890', '0987654321')
agregar_adenda_a_usuario('0987654321', '1234567890', '18-04-2020', "Consulta Regular", 'Una consulta médica regular para evaluar el estado de salud general del paciente, discutir resultados de análisis previos y ajustar cualquier plan de tratamiento existente. Se abordan preguntas del paciente y se proporciona asesoramiento sobre hábitos de vida saludables.')
agregar_adenda_a_usuario('0987654321', '1234567890', '05-01-2022', "Seguimiento Postoperatorio", 'Seguimiento postoperatorio para revisar la recuperación después de una intervención quirúrgica. Se evalúan los signos vitales, se inspeccionan las incisiones y se discuten los próximos pasos en el proceso de recuperación. Se brinda apoyo emocional y se responden preguntas del paciente.')
agregar_adenda_a_usuario('0987654321', '1234567890', '06-12-2023', "Sesión de Consejería Nutricional", 'Sesión especializada para discutir y desarrollar un plan de alimentación personalizado. Se revisan las preferencias alimenticias, se establecen metas nutricionales y se proporciona educación sobre hábitos alimenticios saludables para mejorar el bienestar general.')

eliminar_usuario_por_documento("1092524481")
eliminar_usuario_por_documento("88152239")
eliminar_usuario_por_documento("27897251")
agregar_usuario("1092524481", "123", "profesionalSalud", "Jefferson Hernandez", "20", "3023464345", "Masculino", "https://i.ibb.co/ZGqCFwb/carlitos.png")
agregar_usuario("88152239", "123", "paciente", "Luis Andres Garcia", "45", "3208410532", "Masculino", "https://i.ibb.co/BsMgQnH/image-2023-10-20-102702811.png")
agregar_usuario("27897251", "123", "director", "Claudia Patricia Suarez", "50", "3043757337", "Femenino", "https://i.ibb.co/3ydfwNR/image-2023-10-20-102845276.png")

# POBLACIÓN DE DATOS

import random
from faker import Faker

def generarsusarios():
    faker = Faker()
    registro_documentos = set()
    documento = str(random.randint(1000000000, 9999999999))

    while documento in registro_documentos:
            documento = str(random.randint(1000000000, 9999999999))

    registro_documentos.add(documento)
    clave = "123"
    tipo = random.choice(['paciente','profesionalSalud', 'paciente', 'paciente' ])
    nombre = faker.name()
    edad = str(random.randint(20, 40))
    telefono = str(random.randint(3000000000, 3139999999))
    sexo = random.choice(['masculino','femenino'])
    foto = nombre + ".png"

    agregar_usuario(documento,clave,tipo,nombre,edad,telefono,sexo,foto)

#for _ in range(10000):
#      generarsusarios()

print("> Base de datos inicializada con éxito")
print("")