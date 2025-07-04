from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Usuario, Tutor, Estudiante, Materia, Nivel, TutorMateria, Clase, Seguimiento, Pago, Valoracion, Ubicacion, MensajeClase


def home(request):
    return render(request, 'home.html')


def listar_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/index.html', {'usuarios': usuarios})


def crear_usuarios(request):
    return render(request, 'usuarios/crearUsuarios.html')


def guardar_usuarios(request):
    nombre = request.POST['nombre']
    apellido = request.POST['apellido']
    correo = request.POST['correo']
    telefono = request.POST['telefono']
    password = request.POST['password']
    fecha = request.POST['fecha']
    logo = request.FILES.get('logo')
    rol = request.POST.get('rol')  # Asegúrate que venga en el form

    usuario = Usuario.objects.create(
        nombre=nombre,
        apellido=apellido,
        correo=correo,
        telefono=telefono,
        password_hash=password,
        fecha_registro=fecha,
        logo=logo,
        rol=rol,
    )

    # Gestionar las relaciones Tutor/Estudiante según rol
    if rol == 'tutor':
        if not hasattr(usuario, 'tutor'):
            Tutor.objects.create(usuario=usuario)
        if hasattr(usuario, 'estudiante'):
            usuario.estudiante.delete()
    elif rol == 'estudiante':
        if not hasattr(usuario, 'estudiante'):
            Estudiante.objects.create(usuario=usuario)
        if hasattr(usuario, 'tutor'):
            usuario.tutor.delete()
    else:
        # admin u otro rol: borrar ambos si existen
        if hasattr(usuario, 'tutor'):
            usuario.tutor.delete()
        if hasattr(usuario, 'estudiante'):
            usuario.estudiante.delete()

    messages.success(request, f'Usuario {nombre} creado exitosamente')
    return redirect('/listar-usuarios')


def editar_usuarios(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    return render(request, 'usuarios/editarUsuarios.html', {'usuarios': usuario})


def procesar_info_usuarios(request):
    id = request.POST['id']
    nombre = request.POST['nombre']
    apellido = request.POST['apellido']
    correo = request.POST['correo']
    telefono = request.POST['telefono']
    password = request.POST['password']
    fecha = request.POST['fecha']
    logo = request.FILES.get('logo')
    rol = request.POST.get('rol')

    usuario = get_object_or_404(Usuario, id=id)
    usuario.nombre = nombre
    usuario.apellido = apellido
    usuario.correo = correo
    usuario.telefono = telefono
    usuario.password_hash = password
    usuario.fecha_registro = fecha
    if logo:
        usuario.logo = logo
    usuario.rol = rol
    usuario.save()

    # Gestionar las relaciones Tutor/Estudiante según rol
    if rol == 'tutor':
        if not hasattr(usuario, 'tutor'):
            Tutor.objects.create(usuario=usuario)
        if hasattr(usuario, 'estudiante'):
            usuario.estudiante.delete()
    elif rol == 'estudiante':
        if not hasattr(usuario, 'estudiante'):
            Estudiante.objects.create(usuario=usuario)
        if hasattr(usuario, 'tutor'):
            usuario.tutor.delete()
    else:
        if hasattr(usuario, 'tutor'):
            usuario.tutor.delete()
        if hasattr(usuario, 'estudiante'):
            usuario.estudiante.delete()

    messages.success(request, f'Usuario {nombre} actualizado exitosamente')
    return redirect('/listar-usuarios')


def eliminar_usuarios(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    nombre = usuario.nombre
    usuario.delete()
    messages.success(request, f'Usuario {nombre} eliminado correctamente')
    return redirect('/listar-usuarios')

#Tutores

def listar_tutores(request):
    tutores=Tutor.objects.select_related('usuario').all()
    return render(request,'tutores/index.html',{'tutores':tutores})

def crear_tutores(request):
    return render(request,'tutores/crearTutores.html')

def guardar_tutores(request):
    if request.method == 'POST':
        try:
            # Crear usuario primero
            usuario = Usuario.objects.create(
                nombre=request.POST['nombre'],
                apellido=request.POST['apellido'],
                correo=request.POST['correo'],
                telefono=request.POST['telefono'],
                password_hash=request.POST['password'],
                fecha_registro=request.POST['fecha'],
                logo=request.FILES.get('logo'),
                rol='tutor'  # Rol fijo para tutores
            )
            
            # Crear el tutor asociado
            tutor = Tutor.objects.create(
                usuario=usuario,
                documento=request.FILES.get('documento')
            )
            
            messages.success(request, f'Tutor {usuario.nombre} creado exitosamente')
            return redirect('/listar-tutores')
            
        except Exception as e:
            messages.error(request, f'Error al crear tutor: {str(e)}')
            return redirect('/crear-tutores')
    
    return render(request, 'tutores/crearTutores.html')

#estudiantes

def listar_estudiantes(request):
    estudiantes=Estudiante.objects.select_related('usuario').all()
    return render(request, 'estudiantes/index.html', {'estudiantes': estudiantes})

def crear_estudiantes(request):
    return render(request,'estudiantes/crearEstudiantes.html')

def guardar_estudiantes(request):
    if request.method == 'POST':
        try:
            # Crear usuario primero
            usuario = Usuario.objects.create(
                nombre=request.POST['nombre'],
                apellido=request.POST['apellido'],
                correo=request.POST['correo'],
                telefono=request.POST['telefono'],
                password_hash=request.POST['password'],
                fecha_registro=request.POST['fecha'],
                logo=request.FILES.get('logo'),
                rol='tutor'  # Rol fijo para tutores
            )
            
            # Crear el tutor asociado
            estudiante = Estudiante.objects.create(
                usuario=usuario,
                documento=request.FILES.get('documento')
            )
            
            messages.success(request, f'estudiante {usuario.nombre} creado exitosamente')
            return redirect('/listar-estudiantes')
            
        except Exception as e:
            messages.error(request, f'Error al crear estudiante: {str(e)}')
            return redirect('/crear-estudiantes')
    
    return render(request, 'estudiantes/crearEstudiantes.html')
def eliminar_estudiantes(request,id):
    usuario = get_object_or_404(Usuario, id=id, rol='estudiante')
    nombre=usuario.nombre
    try:
        estudiante=Estudiante.objects.get(usuario=usuario)
        estudiante.delete()
    except Estudiante.DoesNotExist:
        pass
    usuario.delete()
    messages.success(request,f'El estudiante{nombre} ha sido eliminado correctamente')
    return redirect('/listar-usuarios')

def editar_estudiantes(request,id):
    pass
def procesar_info_estudiantes(request):
    pass