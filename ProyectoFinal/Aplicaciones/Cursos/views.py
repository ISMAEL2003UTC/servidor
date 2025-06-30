from django.shortcuts import render

from .models import Usuario, Tutor, Estudiante, Materia, Nivel, TutorMateria, Clase,Seguimiento, Pago, Valoracion, Ubicacion, MensajeClase
#IMPORTANDO COMPONENTE PARA MENSAJE DE CONFIRMACION
from django.contrib import messages


# Create your views here.
def home(request):
    return render(request,'plantilla.html')