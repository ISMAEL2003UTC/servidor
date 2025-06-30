from django.shortcuts import render, redirect

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
def guardar_usuarios(request):
    nombre=request.POST['nombre']
    apellido=request.POST['apellido']
    correo=request.POST['correo']
    telefono=request.POST['telefono']
    password=request.POST['password']
    fecha=request.POST['fecha']
    logo=request.FILES.get('logo')
    Usuario.objects.create(
        nombre=nombre,
        apellido=apellido,
        correo=correo,
        telefono=telefono,
        password_hash=password,
        fecha_registro=fecha,
        logo=logo
    )
    messages.success(request,f'Usuario {nombre} creado exitosamente')
    return redirect('/listar-usuarios')