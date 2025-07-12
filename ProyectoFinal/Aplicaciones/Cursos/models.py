from django.db import models
from django.core.exceptions import ValidationError

class Usuario(models.Model):
    ROLES = [
        ('tutor', 'Tutor'),
        ('estudiante', 'Estudiante'),
        ('admin', 'Administrador'),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    password_hash = models.TextField()
    fecha_registro = models.DateTimeField(auto_now_add=True)
    logo = models.FileField(upload_to='usuarios', null=True, blank=True)
    rol = models.CharField(max_length=20, choices=ROLES)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.rol})"

    def clean(self):
        # Validar que el rol coincida con las relaciones
        if hasattr(self, 'tutor') and self.rol != 'tutor':
            raise ValidationError("El rol debe ser 'tutor' si existe relación con Tutor")
        if hasattr(self, 'estudiante') and self.rol != 'estudiante':
            raise ValidationError("El rol debe ser 'estudiante' si existe relación con Estudiante")

class Tutor(models.Model):
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'tutor'}  # Solo permite usuarios con rol tutor
    )
    documento = models.FileField(upload_to='documentos_tutores', null=True, blank=True)

    def __str__(self):
        return f"Tutor: {self.usuario}"

    def save(self, *args, **kwargs):
        # Asegurar que el usuario tenga el rol correcto
        if self.usuario.rol != 'tutor':
            self.usuario.rol = 'tutor'
            self.usuario.save()
        super().save(*args, **kwargs)

class Estudiante(models.Model):
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'estudiante'}  # Solo permite usuarios con rol estudiante
    )
    documento = models.FileField(upload_to='documentos_estudiantes', null=True, blank=True)

    def __str__(self):
        return f"Estudiante: {self.usuario}"

    def save(self, *args, **kwargs):
        # Asegurar que el usuario tenga el rol correcto
        if self.usuario.rol != 'estudiante':
            self.usuario.rol = 'estudiante'
            self.usuario.save()
        super().save(*args, **kwargs)

class Materia(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    logo = models.FileField(upload_to='materias', null=True, blank=True)
    documento = models.FileField(upload_to='documentos_materias', null=True, blank=True)

    def __str__(self):
        return self.nombre


class Nivel(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


# Materias que imparte cada tutor por nivel
class TutorMateria(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE)
    precio_hora = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('tutor', 'materia', 'nivel')

    def __str__(self):
        return f"{self.tutor} - {self.materia} ({self.nivel})"


class Clase(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    tutor_materia = models.ForeignKey(TutorMateria, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    link_jitsi = models.URLField(blank=True, null=True)
    class Meta:
        # Aquí está la clave: la combinación de estos tres campos debe ser única
        unique_together = ('tutor_materia', 'fecha', 'hora_inicio')
    def __str__(self):
        return f"Clase {self.id} - {self.fecha} - {self.estado}"


class Seguimiento(models.Model):
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)
    observaciones = models.TextField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Seguimiento Clase {self.clase_id}"


class Pago(models.Model):
    ESTADOS_PAGO = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('fallido', 'Fallido'),
    ]
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=6, decimal_places=2)
    fecha_pago = models.DateTimeField(blank=True, null=True)
    metodo_pago = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_PAGO, default='pendiente')

    def __str__(self):
        return f"Pago Clase {self.clase_id} - {self.estado}"


class Valoracion(models.Model):
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)
    puntuacion = models.IntegerField()
    comentario = models.TextField(blank=True, null=True)

    def clean(self):
        if not (1 <= self.puntuacion <= 5):
            raise ValidationError('La puntuación debe estar entre 1 y 5')

    def __str__(self):
        return f"Valoración Clase {self.clase_id}"


class Ubicacion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    direccion = models.TextField()
    barrio = models.CharField(max_length=100, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Ubicación de {self.usuario}"


class MensajeClase(models.Model):
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)
    remitente = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mensaje de {self.remitente} en Clase {self.clase_id}"
