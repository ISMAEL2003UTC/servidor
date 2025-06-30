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


def editar_usuarios(request,id):
    usuarios=Usuario.objects.get(id=id)
    return render(request,'usuarios/editarUsuarios.html',{'usuarios':usuarios})

def procesar_info_usuarios(request):
    id=request.POST['id']
    nombre=request.POST['nombre']
    apellido=request.POST['apellido']
    correo=request.POST['correo']
    telefono=request.POST['telefono']
    password=request.POST['password']
    fecha=request.POST['fecha']
    logo=request.FILES.get('logo')
    
    usuario=Usuario.objects.get(id=id)
    usuario.nombre=nombre
    usuario.apellido=apellido
    usuario.correo=correo
    usuario.telefono=telefono
    usuario.password_hash=password
    usuario.fecha_registro=fecha
    if logo:
        usuario.logo = logo
    usuario.save()
    return redirect('/listar-usuarios')
