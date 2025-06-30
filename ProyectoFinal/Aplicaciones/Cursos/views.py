from django.shortcuts import render

from .models import Usuario, Tutor, Estudiante, Materia, Nivel, TutorMateria, Clase,Seguimiento, Pago, Valoracion, Ubicacion, MensajeClase
#IMPORTANDO COMPONENTE PARA MENSAJE DE CONFIRMACION
from django.contrib import messages


# Create your views here.
def home(request):
    return render(request,'plantilla.html')
def listar_usuarios(request):
    usuarios=Usuario.objects.all()
    return render(request,'usuarios/index.html',{'usuarios':usuarios})
def crear_usuarios(request):
    return render(request,'usuarios/crearUsuarios.html')