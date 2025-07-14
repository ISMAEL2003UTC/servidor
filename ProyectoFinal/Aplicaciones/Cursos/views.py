from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.contrib import messages
import os
from django.db import IntegrityError
from datetime import datetime
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from .models import Usuario, Tutor, Estudiante, Materia, Nivel, TutorMateria, Clase, Seguimiento, Pago, Valoracion, Ubicacion, MensajeClase

#login
from django.contrib.auth.hashers import make_password


def login_view(request):
    if request.method == 'POST':
        correo = request.POST['correo']
        clave = request.POST['clave']

        try:
            usuario = Usuario.objects.get(correo=correo, password_hash=clave)

            request.session['usuario_id'] = usuario.id
            request.session['rol'] = usuario.rol
            request.session['nombre'] = usuario.nombre
            request.session['correo']=usuario.correo
            #manejo de imagen de perfil
            if usuario.logo:
                request.session['logo_url']=usuario.logo.url
            else:
                request.session['logo_url']='/static/img/default-user.png'

            if usuario.rol == 'admin':
                return redirect('/listar-usuarios')
            elif usuario.rol == 'tutor':
                return redirect('/listar-tutores-materias')
            else:
                return redirect('/solicitar-clase')
        except Usuario.DoesNotExist:
            messages.error(request, 'Correo o contraseña incorrectos.')

    return render(request, 'login.html')

def registro(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        correo = request.POST['correo']
        telefono = request.POST['telefono']
        password = request.POST['password']
        rol = request.POST['rol']  # 'estudiante' o 'tutor'

        try:
            # Verificar si el correo ya existe
            if Usuario.objects.filter(correo=correo).exists():
                messages.error(request, 'Este correo ya está registrado.')
                return redirect('/registro')

            # Crear el usuario
            usuario = Usuario.objects.create(
                nombre=nombre,
                apellido=apellido,
                correo=correo,
                telefono=telefono,
                password_hash=password,
                fecha_registro=datetime.now().strftime('%Y-%m-%d'),
                rol=rol
            )

            # Crear el perfil según el rol
            if rol == 'tutor':
                Tutor.objects.create(usuario=usuario)
            elif rol == 'estudiante':
                Estudiante.objects.create(usuario=usuario)
            else:
                rol == 'admin'
                Usuario.objects.create(usuario=usuario)

            messages.success(request, 'Registro exitoso. Por favor inicia sesión.')
            return redirect('/login')

        except Exception as e:
            messages.error(request, f'Error en el registro: {str(e)}')
            return redirect('/registro')

    return render(request, 'registrar.html')

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
                from_email='marlon.acosta9259@utc.edu.ec',
                recipient_list=[correo],
                fail_silently=False
            )
            messages.success(request, 'Revisa tu correo electrónico.')
        except Usuario.DoesNotExist:
            messages.error(request, 'El correo no está registrado.')
    return render(request, 'recuperar_contrasena.html')

def home(request):
    if 'usuario_id' not in request.session:
        return redirect('login')  # Redirige al login si no ha iniciado sesión
    
    return render(request, 'home.html')


# Función para verificar sesión y rol tutor
def tutor_logueado(request):
    usuario_id = request.session.get('usuario_id')
    rol = request.session.get('rol')
    if usuario_id and rol == 'tutor':
        return usuario_id
    return None

#usuarios
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



def eliminar_tutores(request,id):
    usuario_id = request.session.get('usuario_id')
    rol = request.session.get('rol')

    if not usuario_id or rol != 'admin':
        messages.error(request, 'Debes iniciar sesión como Administrador')
        return redirect('/login')
    usuario=get_object_or_404(Usuario,id=id,rol='tutor')
    nombre=usuario.nombre
    try:
        tutor=Tutor.objects.get(usuario=usuario)
        tutor.delete()
    except Tutor.DoesNotExist:
        pass
    usuario.delete()
    messages.success(request,f'Tutor {nombre} eliminador correctamente')
    return redirect('/listar-tutores')

def editar_tutores(request,id):
    usuario_id = request.session.get('usuario_id')
    rol = request.session.get('rol')

    if not usuario_id or rol != 'admin':
        messages.error(request, 'Debes iniciar sesión como Administrador')
        return redirect('/login')
    usuarios=get_object_or_404(Usuario,id=id,rol='tutor')
    tutores=get_object_or_404(Tutor,usuario=usuarios)
    return render(request,'tutores/editarTutores.html',{
        'usuarios':usuarios,
        'tutores':tutores
    })

def procesar_info_tutores(request):
    usuario_id = request.session.get('usuario_id')
    rol = request.session.get('rol')

    if not usuario_id or rol != 'admin':
        messages.error(request, 'Debes iniciar sesión como Administrador')
        return redirect('/login')
    if request.method == 'POST':
        id_usuario = request.POST['id']
        usuario = Usuario.objects.get(id=id_usuario)
        tutor = Tutor.objects.get(usuario=usuario)

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
            if tutor.documento:
                if os.path.isfile(tutor.documento.path):
                    os.remove(tutor.documento.path)
            tutor.documento = request.FILES['documento']
        
        tutor.save()

    return redirect('/listar-tutores')

def solicitudes_clases_tutores(request):
    usuario_id= tutor_logueado(request)
    if not usuario_id:
        messages.error(request,"Debes iniciar sesion como tutor")
        return redirect('/login')
    tutor = get_object_or_404(Tutor,usuario__id=usuario_id)
    clases=Clase.objects.filter(tutor_materia__tutor=tutor, estado='pendiente').select_related(
        'estudiante__usuario','tutor_materia__materia','tutor_materia__nivel'
        
    )
    return render(request,'tutores/solicitudesClases.html',{
        'clases':clases
    })

'''def cambiar_estado_clase(request,clase_id,nuevo_estado):
    usuario_id=tutor_logueado(request)
    if not usuario_id:
        messages.error(request,'Debes iniciar session como tutor')
        return redirect('/login')
    clase=get_object_or_404(Clase,id=clase_id,tutor_materia__tutor__usuario_id=usuario_id)
    if nuevo_estado in ['confirmada','cancelada']:
        clase.estado = nuevo_estado
        clase.save()
        messages.success(request,f'clase marcada  {nuevo_estado}')
    else:
        messages.error(request,'Estado no valido')

    return redirect('/solicitudes-clases-tutores') '''

'''def cambiar_estado_clase(request, clase_id, nuevo_estado):
    usuario_id = tutor_logueado(request)
    if not usuario_id:
        messages.error(request, 'Debes iniciar sesión como tutor')
        return redirect('/login')

    # Verificamos que la clase pertenezca al tutor logueado
    clase = get_object_or_404(Clase, id=clase_id, tutor_materia__tutor__usuario_id=usuario_id)

    if nuevo_estado not in ['pendiente', 'confirmada', 'cancelada']:
        messages.error(request, 'Estado no válido')
        return redirect('/solicitudes-clases-tutores')

    if nuevo_estado == 'confirmada' and not clase.link_jitsi:
        # Crear link Jitsi dinámicamente
        base_url = "https://meet.jit.si/"
        sala = f"educatec_clase_{clase.id}"
        clase.link_jitsi = f"{base_url}{sala}"

        # Enviar correo al estudiante (comentado, pero listo para usar)
        
        send_mail(
            subject='Tu clase ha sido confirmada',
            message=f'Se ha confirmado tu clase . Únete aquí: {clase.link_jitsi}',
            from_email='marlon.acosta9259@utc.edu.ec',
            recipient_list=[clase.estudiante.usuario.correo],
            fail_silently=True,
        )
        

    clase.estado = nuevo_estado
    clase.save()
    messages.success(request, f'Clase marcada como {nuevo_estado}')
    return redirect('/solicitudes-clases-tutores')
'''
def cambiar_estado_clase(request, clase_id, nuevo_estado):
    usuario_id = request.session.get('usuario_id')
    
    if not usuario_id or request.session.get('rol') != 'tutor':
        messages.error(request, 'Debes iniciar sesión como tutor.')
        return redirect('/login')

    # Obtiene la clase y precarga datos; si no existe o no pertenece al tutor, devuelve 404
    clase = get_object_or_404(
        Clase.objects.select_related(
            'tutor_materia__tutor__usuario', 
            'tutor_materia__materia',
            'estudiante__usuario'
        ), 
        id=clase_id, 
        tutor_materia__tutor__usuario_id=usuario_id
    )

    if nuevo_estado not in ['pendiente', 'confirmada', 'cancelada']:
        messages.error(request, 'Estado no válido.')
        return redirect('/solicitudes-clases-tutores')

    if nuevo_estado == 'confirmada' and not clase.link_jitsi:
        clase.link_jitsi = f"https://meet.jit.si/educatec_clase_{clase.id}"
        
        # Prepara y envía el correo directamente
        send_mail(
            subject=f'Clase de {clase.tutor_materia.materia.nombre} confirmada con {clase.tutor_materia.tutor.usuario.nombre} {clase.tutor_materia.tutor.usuario.apellido}',
            message=(
                f'Hola {clase.estudiante.usuario.nombre},\n\n'
                f'Tu clase de **{clase.tutor_materia.materia.nombre}** con el tutor **{clase.tutor_materia.tutor.usuario.nombre} {clase.tutor_materia.tutor.usuario.apellido}** '
                f'ha sido confirmada.\n\n'
                f'Detalles de la clase:\n'
                f'  Materia: {clase.tutor_materia.materia.nombre}\n'
                f'  Hora: {clase.hora_inicio.strftime("%H:%M")}\n'
                f'  Tutor: {clase.tutor_materia.tutor.usuario.nombre} {clase.tutor_materia.tutor.usuario.apellido}\n\n'
                f'Para unirte a tu clase, haz clic en el siguiente enlace:\n'
                f'{clase.link_jitsi}\n\n'
                f'¡Te esperamos en Educatec!'
            ),
            from_email='marlon.acosta9259@utc.edu.ec',
            recipient_list=[clase.estudiante.usuario.correo],
            fail_silently=True,
        )
        
    clase.estado = nuevo_estado
    clase.save()
    messages.success(request, f'Clase marcada como {nuevo_estado}.')
    return redirect('/solicitudes-clases-tutores')
    
def clases_confirmadas_tutores(request):
    usuario_id = request.session.get('usuario_id')
    rol=request.session.get('rol')

    if not usuario_id or rol != 'tutor':
        messages.error(request,'Debes iniciar session como tutor para ver tus clases ')
        return redirect('/login')
    tutor = get_object_or_404(Tutor,usuario__id=usuario_id)
    clases_confirmadas=Clase.objects.filter(
        tutor_materia__tutor=tutor,
        estado='confirmada'
    ).select_related(
        'estudiante__usuario',#para acceder al nombr del estudiante
        'tutor_materia__materia'#para acceder al nombre de la materua
    ).order_by('fecha','hora_inicio') #ordenar por fecha y hora 

    return render(request,'tutores/misMaterias.html',{
        'clases':clases_confirmadas
    })
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
                rol='estudiante'  # Rol fijo para estudiantes
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
    return redirect('/listar-estudiantes')

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

# Paso 1: Vista que muestra las materias
def seleccionar_materia(request):
    if request.session.get('rol') != 'estudiante':
        return redirect('/login')
    
    materias = Materia.objects.all()
    return render(request, 'estudiantes/seleccionar_materia.html', {'materias': materias})


# Paso 2: Vista que muestra detalle para solicitar clase
def detalle_solicitud_clase(request, materia_id):
    
    materia = get_object_or_404(Materia, id=materia_id)
    
    # niveles y tutores disponibles para esa materia
    tutores_materia = TutorMateria.objects.filter(materia_id=materia_id).select_related('tutor__usuario', 'nivel')
    niveles = {tm.nivel for tm in tutores_materia}  # Evitar niveles duplicados

    return render(request, 'estudiantes/detalle_solicitud_clase.html', {
        'materia': materia,
        'tutores_materia': tutores_materia,
        'niveles': niveles
    })


# Paso 3: Guardar clase desde detalle
''' def guardar_clase_detalle(request):
    if request.method == 'POST':
        estudiante = get_object_or_404(Estudiante, usuario__id=request.session['usuario_id'])

        tutor = get_object_or_404(Tutor, id=request.POST['tutor_id'])
        materia = get_object_or_404(Materia, id=request.POST['materia_id'])
        nivel = get_object_or_404(Nivel, id=request.POST['nivel_id'])
        fecha = request.POST['fecha']
        hora = request.POST['hora']

        tm = get_object_or_404(TutorMateria, tutor=tutor, materia=materia, nivel=nivel)

        Clase.objects.create(
            estudiante=estudiante,
            tutor_materia=tm,
            fecha=fecha,
            hora_inicio=hora,
            hora_fin=hora,  # Puedes ajustar duración
            estado='pendiente'
        )
        messages.success(request, 'Clase solicitada correctamente.')
        return redirect('/listar-estudiantes')
'''
def guardar_clase_detalle(request):
    if request.method == 'POST':
        estudiante = get_object_or_404(Estudiante, usuario__id=request.session['usuario_id'])

        tutor = get_object_or_404(Tutor, id=request.POST['tutor_id'])
        materia = get_object_or_404(Materia, id=request.POST['materia_id'])
        nivel = get_object_or_404(Nivel, id=request.POST['nivel_id']) # <-- CORRECCIÓN AQUÍ

        try:
            fecha_obj = datetime.strptime(request.POST['fecha'], '%Y-%m-%d').date()
            hora_obj = datetime.strptime(request.POST['hora'], '%H:%M').time()
        except ValueError:
            messages.error(request, 'Formato de fecha u hora incorrecto. Usa AAAA-MM-DD y HH:MM.')
            return redirect('/solicitar-clase', materia_id=materia.id)

        tm = get_object_or_404(TutorMateria, tutor=tutor, materia=materia, nivel=nivel)

        if Clase.objects.filter(
            tutor_materia__tutor=tutor,
            fecha=fecha_obj,
            hora_inicio=hora_obj
        ).exists():
            messages.error(request, 'Ya existe una clase programada con este tutor a esta hora y fecha. Por favor, elige otro horario.')
            return redirect('/solicitar-clase', materia_id=materia.id)

        try:
            Clase.objects.create(
                estudiante=estudiante,
                tutor_materia=tm,
                fecha=fecha_obj,
                hora_inicio=hora_obj,
                hora_fin=hora_obj,
                estado='pendiente'
            )
            messages.success(request, 'Clase solicitada correctamente. Esperando confirmación del tutor.')
            return redirect('/solicitar-clase')
        except IntegrityError:
            messages.error(request, 'Este horario ya no está disponible. Por favor, elige otro.')
            return redirect('/solicitar-clase', materia_id=materia.id)
        except Exception as e:
            messages.error(request, f'Ocurrió un error inesperado al solicitar la clase: {e}')
            return redirect('/solicitar-clase', materia_id=materia.id)

    return redirect('/solicitar-clase')

#nuevo
def clases_confirmadas_estudiante(request):
    usuario_id = request.session.get('usuario_id')
    rol = request.session.get('rol')

    if not usuario_id or rol != 'estudiante':
        messages.error(request, 'Debes iniciar sesión como estudiante')
        return redirect('/login')

    estudiante = get_object_or_404(Estudiante, usuario__id=usuario_id)

    clases_confirmadas = Clase.objects.filter(
        estudiante=estudiante,
        estado='confirmada'
    ).order_by('fecha', 'hora_inicio')

    return render(request, 'estudiantes/clases_confirmadas.html', {'clases': clases_confirmadas})

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

def listar_tutores_materias(request):
    usuario_id = tutor_logueado(request)
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión como tutor para acceder aquí.")
        return redirect('/login')

    tutor = get_object_or_404(Tutor, usuario__id=usuario_id)
    tutor_materias = TutorMateria.objects.filter(tutor=tutor).select_related('materia', 'nivel')

    return render(request, 'tutores_materias/listar_tutores_materias.html', {
        'tutor_materias': tutor_materias,
    })



def crear_tutores_materias(request):
    usuario_id = tutor_logueado(request)
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión como tutor para acceder aquí.")
        return redirect('/login')

    tutor = get_object_or_404(Tutor, usuario__id=usuario_id)
    materias = Materia.objects.all()
    niveles = Nivel.objects.all()

    return render(request, 'tutores_materias/crear_tutores_materias.html', {
        'materias': materias,
        'niveles': niveles,
    })


def guardar_tutores_materias(request):
    if request.method == 'POST':
        usuario_id = tutor_logueado(request)
        if not usuario_id:
            messages.error(request, "Debes iniciar sesión como tutor para realizar esta acción.")
            return redirect('/login')

        tutor = get_object_or_404(Tutor, usuario__id=usuario_id)

        materia_id = request.POST.get('materia_id')
        nivel_id = request.POST.get('nivel_id')
        precio_hora = request.POST.get('precio_hora')

        if not materia_id or not nivel_id or not precio_hora:
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect('/crear-tutores-materias')

        # Validar si la combinación ya existe para evitar duplicados
        existe = TutorMateria.objects.filter(
            tutor=tutor,
            materia_id=materia_id,
            nivel_id=nivel_id
        ).exists()

        if existe:
            messages.error(request, "Ya tienes asociada esta materia y nivel.")
            return redirect('/crear-tutores-materias')

        TutorMateria.objects.create(
            tutor=tutor,
            materia_id=materia_id,
            nivel_id=nivel_id,
            precio_hora=precio_hora
        )

        messages.success(request, "Materia y nivel asociados correctamente.")
        return redirect('/listar-tutores-materias')

    return redirect('/crear-tutores-materias')

def editar_tutores_materias(request, id):
    usuario_id = tutor_logueado(request)
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión como tutor para acceder aquí.")
        return redirect('/login')

    tutor_materia = get_object_or_404(TutorMateria, id=id, tutor__usuario__id=usuario_id)
    materias = Materia.objects.all()
    niveles = Nivel.objects.all()

    return render(request, 'tutores_materias/editar_tutores_materias.html', {
        'tutor_materia': tutor_materia,
        'materias': materias,
        'niveles': niveles,
    })

def procesar_info_tutores_materias(request):
    if request.method == 'POST':
        usuario_id = tutor_logueado(request)
        if not usuario_id:
            messages.error(request, "Debes iniciar sesión como tutor para realizar esta acción.")
            return redirect('/login')

        id = request.POST.get('id')
        tutor_materia = get_object_or_404(TutorMateria, id=id, tutor__usuario__id=usuario_id)
        
        materia_id = request.POST.get('materia_id')
        nivel_id = request.POST.get('nivel_id')
        precio_hora = request.POST.get('precio_hora')

        # Validar si la nueva combinación ya existe (excluyendo el registro actual)
        existe = TutorMateria.objects.filter(
            tutor=tutor_materia.tutor,
            materia_id=materia_id,
            nivel_id=nivel_id
        ).exclude(id=id).exists()

        if existe:
            messages.error(request, "Ya tienes asociada esta materia y nivel.")
            return redirect(f'/editar-tutores-materias/{id}')

        # Actualizar los datos
        tutor_materia.materia_id = materia_id
        tutor_materia.nivel_id = nivel_id
        tutor_materia.precio_hora = precio_hora
        tutor_materia.save()

        messages.success(request, "Asociación actualizada correctamente.")
        return redirect('/listar-tutores-materias')

    return redirect('/listar-tutores-materias')

def eliminar_tm(request, id):
    tm = get_object_or_404(TutorMateria, id=id)
    nombre_materia = tm.materia.nombre  # Obtenemos el nombre de la materia
    
    tm.delete()
    messages.success(request, f'Tu materia {nombre_materia} ha sido eliminada correctamente')
    # Aquí debes redirigir a alguna vista, por ejemplo:
    return redirect('/listar-tutores-materias')

