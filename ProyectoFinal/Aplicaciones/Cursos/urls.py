from django.urls import path
from . import views
urlpatterns = [
    path('', views.home),
    path('listar-usuarios',views.listar_usuarios),
    path('crear-usuarios',views.crear_usuarios),
    path('guardar-usuarios',views.guardar_usuarios),
    path('eliminar-usuarios/<id>',views.eliminar_usuarios),
    path('editar-usuarios/<id>',views.editar_usuarios),
    path('procesar-info-usuarios',views.procesar_info_usuarios),
    #tutores
    path('listar-tutores',views.listar_tutores),
    path('crear-tutores',views.crear_tutores),
    path('guardar-tutores',views.guardar_tutores),
    #path('eliminar-usuarios/<id>',views.eliminar_usuarios),
    #path('editar-usuarios/<id>',views.editar_usuarios),
    #path('procesar-info-usuarios',views.procesar_info_usuarios)

    #estudiantes
    path('listar-estudiantes',views.listar_estudiantes),
    path('crear-estudiantes',views.crear_estudiantes),
    path('guardar-estudiantes',views.guardar_estudiantes),
    path('eliminar-estudiantes/<id>',views.eliminar_estudiantes),
    path('editar-estudiantes/<id>',views.editar_estudiantes),
    path('procesar-info-estudiantes',views.procesar_info_estudiantes)
]