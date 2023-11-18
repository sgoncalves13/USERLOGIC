import json
import jwt
from django.conf import settings
import hashlib
from secrets import token_bytes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from base64 import urlsafe_b64encode, urlsafe_b64decode
from .models import Usuario, Adenda, HistoriaClinica

def encriptarMensaje(mensaje, llave):

    backend = default_backend()
    cipher = Cipher(algorithms.AES(llave), modes.CFB, backend=backend)
    encryptor = cipher.encryptor()

    ciphertext = encryptor.update(mensaje.encode()) + encryptor.finalize()

    return urlsafe_b64encode(ciphertext).decode()

def obtener_usuario_por_documento(documento):
    try:
        usuario = Usuario.objects.get(documento=documento)
        return usuario
    except Usuario.DoesNotExist:
        return None
    
def eliminar_usuario_por_documento(documento):
    try:
        usuario = Usuario.objects.get(documento=documento)
        usuario.delete()
        return usuario
    except Usuario.DoesNotExist:
        return None
    
def agregar_usuario(documento, clave, tipo, nombre, edad, telefono, sexo, foto):
    usuario = Usuario(
        documento=documento,
        clave=clave,
        tipo=tipo,
        nombre=nombre,
        edad=edad,
        telefono=telefono,
        sexo=sexo,
        foto=foto,
    )
    usuario.save()
    return usuario
    
def agregar_paciente_a_medico(documento_profesional, documento_paciente):
    try:
        profesional = Usuario.objects.get(documento=documento_profesional)
        paciente = Usuario.objects.get(documento=documento_paciente)
        paciente.medico.add(profesional)
        return paciente
    except Usuario.DoesNotExist:
        return None

def agregar_adenda_a_usuario(documento_paciente, documento_profesional, fecha, tipo, descripcion):

    try:
        usuario = Usuario.objects.get(documento=documento_paciente)
        
        if not usuario.medico.filter(documento=documento_profesional).exists():
            return "true"

        if not usuario.historia_clinica:

            nueva_historia_clinica = HistoriaClinica(
                diagnosticos="Ninguno",
                tratamientos="Ninguno",
                notas="Ninguno"
            )
            nueva_historia_clinica.save()
            usuario.historia_clinica = nueva_historia_clinica
            usuario.save()

        adenda = Adenda(fecha=fecha, tipo=tipo, descripcion=descripcion, historia_clinica=usuario.historia_clinica)
        adenda.save()

        return None

    except Usuario.DoesNotExist:
        return "false"

class usuarioAPI(APIView):

    def post(self, request):

        documento = request.data.get("documento")

        try:
            usuario = Usuario.objects.get(documento=documento)
        except Usuario.DoesNotExist:
            return Response({"mensaje": "noexiste"}, status=status.HTTP_200_OK)

        usuario = {
            "documento": usuario.documento,
            "foto": usuario.foto,
            "nombre": usuario.nombre,
            "edad": usuario.edad,
            "telefono": usuario.telefono,
            "sexo": usuario.sexo,
        }

        return Response(usuario, status=status.HTTP_200_OK)
    
class historiaClinicaAPI(APIView):

    def post(self, request):

        try:
            documento_paciente = request.data.get("documento_paciente")
            documento_profesional = request.data.get("documento_profesional")

            paciente = Usuario.objects.get(documento=documento_paciente)

            if documento_profesional is not None:

                if not paciente.medico.filter(documento=documento_profesional).exists():
                    return Response({"mensaje":"true"}, status=status.HTTP_200_OK)

            dict_historiaclinica = {}
            if paciente.historia_clinica:

                historia = paciente.historia_clinica

                dict_historiaclinica["diagnosticos"] = historia.diagnosticos
                dict_historiaclinica["tratamientos"] = historia.tratamientos
                dict_historiaclinica["notas"] = historia.notas

                adendas = Adenda.objects.filter(historia_clinica=historia)
                adendas_list = [
                    {
                        "fecha": adenda.id_adenda,
                        "tipo": adenda.fecha,
                        "descripcion": adenda.descripcion
                    } for adenda in adendas
                ]

                dict_historiaclinica["adendas"] = adendas_list

            llave = token_bytes(32)
            mensaje_decodificado = encriptarMensaje(dict_historiaclinica, llave)

            llave_decodificada = jwt.encode(llave, settings.SECRET_KEY, algorithm="HS256")

            return Response({"llave_codificada":llave_decodificada,"mensaje_codificado":mensaje_decodificado}, status=status.HTTP_200_OK)

        except Usuario.DoesNotExist:
            return Response({}, status=status.HTTP_200_OK)
    
class agregarAdendaAPI(APIView):

    def post(self, request):

        documento_paciente = request.data.get("documento_paciente")
        documento_profesional = request.data.get("documento_profesional")
        fecha = request.data.get("fecha")
        tipo = request.data.get("tipo")
        descripcion = request.data.get("descripcion")

        informacion_adenda = {"documento_paciente": documento_paciente, "documento_profesional": documento_profesional, "fecha": fecha, "tipo": tipo, "descripcion": descripcion}
        informacion_firma = json.dumps(informacion_adenda, sort_keys=True)

        firma_calculada = hashlib.sha256(informacion_firma.encode()).hexdigest()

        firma_mensaje_cifrada = request.data.get("firma")
        decoded_firma = jwt.decode(firma_mensaje_cifrada, settings.SECRET_KEY, algorithms=["HS256"])

        if firma_calculada == decoded_firma:
            mensaje = agregar_adenda_a_usuario(documento_paciente, documento_profesional, fecha, tipo, descripcion)
        else:
            mensaje = "manipulado"

        return Response({"mensaje":mensaje}, status=status.HTTP_200_OK)
    

# Inicialiación de la Base de Datos
eliminar_usuario_por_documento("1234567890")
eliminar_usuario_por_documento("0987654321")
agregar_usuario("1234567890", "123", "profesionalSalud", "Carlos Muñoz", "20", "3164614926", "Masculino", "https://i.ibb.co/ZGqCFwb/carlitos.png")
agregar_usuario("0987654321", "123", "paciente", "Harold Samuel Hernandez", "25", "323232323232", "Masculino", "https://i.ibb.co/ZgNP89g/image-2023-10-20-103230643.png")
agregar_paciente_a_medico('1234567890', '0987654321')

eliminar_usuario_por_documento("1092524481")
eliminar_usuario_por_documento("88152239")
eliminar_usuario_por_documento("27897251")
agregar_usuario("1092524481", "123", "profesionalSalud", "Jefferson Hernandez", "20", "3023464345", "Masculino", "https://i.ibb.co/ZGqCFwb/carlitos.png")
agregar_usuario("88152239", "123", "paciente", "Luis Andres Garcia", "45", "3208410532", "Masculino", "https://i.ibb.co/BsMgQnH/image-2023-10-20-102702811.png")
agregar_usuario("27897251", "123", "director", "Claudia Patricia Suarez", "50", "3043757337", "Femenino", "https://i.ibb.co/3ydfwNR/image-2023-10-20-102845276.png")

print("> Base de datos inicializada con éxito")
print("")