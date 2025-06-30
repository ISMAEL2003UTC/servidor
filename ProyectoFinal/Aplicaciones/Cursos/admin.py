from django.contrib import admin
from .models import (
    Usuario, Tutor, Estudiante, Materia, Nivel, TutorMateria, Clase,
    Seguimiento, Pago, Valoracion, Ubicacion, MensajeClase
)

# Registro sencillo de todos los modelos
admin.site.register(Usuario)
admin.site.register(Tutor)
admin.site.register(Estudiante)
admin.site.register(Materia)
admin.site.register(Nivel)
admin.site.register(TutorMateria)
admin.site.register(Clase)
admin.site.register(Seguimiento)
admin.site.register(Pago)
admin.site.register(Valoracion)
admin.site.register(Ubicacion)
admin.site.register(MensajeClase)
