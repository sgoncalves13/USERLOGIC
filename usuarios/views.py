import json
import jwt
import base64
from django.conf import settings
import hashlib
from secrets import token_bytes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from cryptography.fernet import Fernet
from .models import Usuario, Adenda, HistoriaClinica

def encriptarMensaje(mensaje, llave):
    f = Fernet(llave)
    mensaje_json = json.dumps(mensaje)
    mensaje_cifrado = f.encrypt(mensaje_json.encode()) 
    return mensaje_cifrado

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
        foto=foto,
        nombre=nombre,
        edad=edad,
        telefono=telefono,
        sexo=sexo,
    )
    usuario.save()
    return usuario
    
def asignar_medico_a_paciente(documento_profesional, documento_paciente):
    try:
        profesional = Usuario.objects.get(documento=documento_profesional, tipo='medico')
        paciente = Usuario.objects.get(documento=documento_paciente, tipo='paciente')
        if not paciente.medico:
            paciente.medico = profesional
            paciente.save()
            
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
    
def bytes_a_base64(mensaje_bytes):
    return base64.b64encode(mensaje_bytes).decode('utf-8')

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
                        "fecha": adenda.fecha,
                        "tipo": adenda.tipo,
                        "descripcion": adenda.descripcion
                    } for adenda in adendas
                ]

                dict_historiaclinica["adendas"] = adendas_list

            llave = Fernet.generate_key()
            mensaje_codificado = encriptarMensaje(dict_historiaclinica, llave)
            mensaje_codificado_base64 = bytes_a_base64(mensaje_codificado)

            llave_base64 = bytes_a_base64(llave)
            llave_codificada_jwt = jwt.encode({"llave": llave_base64}, settings.SECRET_KEY, algorithm="HS256")

            return Response({"llave_codificada":llave_codificada_jwt,"mensaje_codificado":mensaje_codificado_base64}, status=status.HTTP_200_OK)

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
    

# Inicialiación de la Base de Datos
eliminar_usuario_por_documento("1234567890")
eliminar_usuario_por_documento("0987654321")
agregar_usuario("1234567890", "123", "profesionalSalud", "Carlos Muñoz", "20", "3164614926", "Masculino", "https://i.ibb.co/ZGqCFwb/carlitos.png")
agregar_usuario("0987654321", "123", "paciente", "Harold Samuel Hernandez", "25", "323232323232", "Masculino", "https://i.ibb.co/ZgNP89g/image-2023-10-20-103230643.png")
asignar_medico_a_paciente('1234567890', '0987654321')

eliminar_usuario_por_documento("1092524481")
eliminar_usuario_por_documento("88152239")
eliminar_usuario_por_documento("27897251")
agregar_usuario("1092524481", "123", "profesionalSalud", "Jefferson Hernandez", "20", "3023464345", "Masculino", "https://i.ibb.co/ZGqCFwb/carlitos.png")
agregar_usuario("88152239", "123", "paciente", "Luis Andres Garcia", "45", "3208410532", "Masculino", "https://i.ibb.co/BsMgQnH/image-2023-10-20-102702811.png")
agregar_usuario("27897251", "123", "director", "Claudia Patricia Suarez", "50", "3043757337", "Femenino", "https://i.ibb.co/3ydfwNR/image-2023-10-20-102845276.png")

print("> Base de datos inicializada con éxito")
print("")