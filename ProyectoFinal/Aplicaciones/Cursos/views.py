from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import os
from django.core.mail import send_mail

from .models import Usuario, Tutor, Estudiante, Materia, Nivel, TutorMateria, Clase, Seguimiento, Pago, Valoracion, Ubicacion, MensajeClase

#login

def login_view(request):
    if request.method == 'POST':
        correo = request.POST['correo']
        clave = request.POST['clave']

        try:
            usuario = Usuario.objects.get(correo=correo, password_hash=clave)

            request.session['usuario_id'] = usuario.id
            request.session['rol'] = usuario.rol
            request.session['nombre'] = usuario.nombre

            if usuario.rol == 'admin':
                return redirect('/admin-dashboard')
            elif usuario.rol == 'tutor':
                return redirect('/listar-tutores')
            else:
                return redirect('/solicitar-clase')
        except Usuario.DoesNotExist:
            messages.error(request, 'Correo o contraseña incorrectos.')

    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    return redirect('/login')


# Simulación recuperación de contraseña
def recuperar_contrasena(request):
    if request.method == 'POST':
        correo = request.POST['correo']
        try:
            usuario = Usuario.objects.get(correo=correo)
            # Simulación: enviar clave (en sistemas reales, se debe enviar enlace temporal o código)
            send_mail(
                subject='Recuperación de contraseña',
                message=f'Tu contraseña es: {usuario.password_hash}',
                from_email='no-reply@educatec.com',
                recipient_list=[correo],
                fail_silently=False
            )
            messages.success(request, 'Revisa tu correo electrónico.')
        except Usuario.DoesNotExist:
            messages.error(request, 'El correo no está registrado.')
    return render(request, 'recuperar_contrasena.html')

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

#Tutores----------------------------------------------------------------------------

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

#estudiantes -------------------------------------------------------------------------

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
    usuario=get_object_or_404(Usuario,id=id,rol='estudiante')
    estudiante=get_object_or_404(Estudiante,usuario=usuario)
    return render(request,'estudiantes/editarEstudiantes.html',{
        'usuarios':usuario,
        'estudiantes':estudiante
    })
def procesar_info_estudiantes(request):
    if request.method == 'POST':
        id_usuario = request.POST['id']
        usuario = Usuario.objects.get(id=id_usuario)
        estudiante = Estudiante.objects.get(usuario=usuario)

        # Actualizar campos del usuario
        usuario.nombre = request.POST['nombre']
        usuario.apellido = request.POST['apellido']
        usuario.correo = request.POST['correo']
        usuario.telefono = request.POST['telefono']
        usuario.password_hash = request.POST['password']
        usuario.fecha_registro = request.POST['fecha']
        # Cambiar logo si se sube nuevo
        if 'logo' in request.FILES:
            if usuario.logo:
                if os.path.isfile(usuario.logo.path):
                    os.remove(usuario.logo.path)
            usuario.logo = request.FILES['logo']
        
        usuario.save()

        # Cambiar documento si se sube nuevo
        if 'documento' in request.FILES:
            if estudiante.documento:
                if os.path.isfile(estudiante.documento.path):
                    os.remove(estudiante.documento.path)
            estudiante.documento = request.FILES['documento']
        
        estudiante.save()

    return redirect('/listar-estudiantes')

#materias ----------------------------------------------------------------
def listar_materias(request):
    materias=Materia.objects.all()
    return render(request,'materias/index.html',{'materias':materias})

def crear_materias(request):
    return render(request,'materias/crearMaterias.html')

def guardar_materias(request):
    nombre=request.POST['nombre']
    descripcion=request.POST['descripcion']
    logo=request.FILES.get('logo')
    documento=request.FILES.get('documento')
    Materia.objects.create(
        nombre=nombre,
        descripcion=descripcion,
        logo=logo,
        documento=documento
    )
    messages.success(request,f'La materia {nombre} ha sido creada exitosamente')
    return redirect('/listar-materias')

def eliminar_usuarios(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    nombre = usuario.nombre
    usuario.delete()
    messages.success(request, f'Usuario {nombre} eliminado correctamente')
    return redirect('/listar-usuarios')

def eliminar_materias(request,id):
    materia=get_object_or_404(Materia,id=id)
    nombre=materia.nombre
    materia.delete()
    messages.success(request,f'la materia {nombre} ha sido eliminada correctamente')
    return redirect('/listar-materias')


def editar_materias(request,id):
    materias=Materia.objects.get(id=id)
    return render(request,'materias/editarMaterias.html',{'materias':materias})

def procesar_info_materias(request):
    id=request.POST['id']
    materias=Materia.objects.get(id=id)
    nombre=request.POST['nombre']
    descripcion=request.POST['descripcion']
    materias.nombre=nombre
    materias.descripcion=descripcion

    if 'logo' in request.FILES:
        if materias.logo:
            if os.path.isfile(materias.logo.path):
                os.remove(materias.logo.path)
        materias.logo = request.FILES['logo']
    
    materias.save()

    # Cambiar documento si se sube nuevo
    if 'documento' in request.FILES:
        if materias.documento:
            if os.path.isfile(materias.documento.path):
                os.remove(materias.documento.path)
        materias.documento = request.FILES['documento']
    
    materias.save()
    return redirect('/listar-materias')


#niveles-----------------------------------------------------

def listar_niveles(request):
    niveles=Nivel.objects.all()
    return render(request,'niveles/index.html',{'niveles':niveles})

def crear_niveles(request):
    return render(request,'niveles/crearNiveles.html')

def guardar_niveles(request):
    nombre=request.POST['nombre']
    descripcion=request.POST['descripcion']
    Nivel.objects.create(
        nombre=nombre,
        descripcion=descripcion
    )

    messages.success(request,f'El nivel {nombre} ha sido creada exitosamente')
    return redirect('/listar-niveles')

def eliminar_niveles(request, id):
    nivel = get_object_or_404(Nivel, id=id)
    nombre = nivel.nombre
    nivel.delete()
    messages.success(request, f'Nivel {nombre} eliminado correctamente')
    return redirect('/listar-niveles')


def editar_niveles(request,id):
    niveles=Nivel.objects.get(id=id)
    return render(request,'niveles/editarNiveles.html',{'niveles':niveles})

def procesar_info_niveles(request):
    id=request.POST['id']
    niveles=Nivel.objects.get(id=id)
    nombre=request.POST['nombre']
    descripcion=request.POST['descripcion']
    niveles.nombre=nombre
    niveles.descripcion=descripcion

    
    niveles.save()
    return redirect('/listar-niveles')

#Asociar Materia-------------------------------------------------------------------------------------

