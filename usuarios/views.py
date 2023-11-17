import json
import jwt
import hashlib
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Usuario, Adenda, HistoriaClinica

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
            respuesta_post = {}
            return Response(respuesta_post, status=status.HTTP_200_OK)

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

        pass
    
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
        firma_mensaje = request.data.get("firma")

        if firma_calculada == firma_mensaje:
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

print("")
print("> Base de datos inicializada con éxito")
print("")