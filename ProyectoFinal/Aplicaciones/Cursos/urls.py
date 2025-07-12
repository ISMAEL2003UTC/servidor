from django.urls import path
from . import views
urlpatterns = [
    #login
    # login y logout
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('recuperar-contrasena', views.recuperar_contrasena, name='recuperar_contrasena'),
    #home
    path('', views.home),
    #usuarios
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
    path('eliminar-tutores/<id>',views.eliminar_tutores),
    path('editar-tutores/<id>',views.editar_tutores),
    path('procesar-info-tutores',views.procesar_info_tutores),
    path('solicitudes-clases-tutores',views.solicitudes_clases_tutores,name='solicitudes_clase_tutor'),
    path('cambiar-estado-clase/<int:clase_id>/<str:nuevo_estado>/', views.cambiar_estado_clase, name='cambiar_estado_clase'),
    path('clases-confirmadas-tutores',views.clases_confirmadas_tutores),

    

    #estudiantes
    path('listar-estudiantes',views.listar_estudiantes),
    path('crear-estudiantes',views.crear_estudiantes),
    path('guardar-estudiantes',views.guardar_estudiantes),
    path('eliminar-estudiantes/<id>',views.eliminar_estudiantes),
    path('editar-estudiantes/<id>',views.editar_estudiantes),
    path('procesar-info-estudiantes',views.procesar_info_estudiantes),
    path('solicitar-clase', views.seleccionar_materia, name='seleccionar-materia'),
    path('detalle-solicitud-clase/<int:materia_id>', views.detalle_solicitud_clase, name='detalle-solicitud-clase'),
    path('guardar-clase-detalle', views.guardar_clase_detalle, name='guardar-clase-detalle'),
    path('clases-confirmadas/', views.clases_confirmadas_estudiante, name='clases_confirmadas'),
    #materias
    path('listar-materias',views.listar_materias),
    path('crear-materias',views.crear_materias),
    path('guardar-materias',views.guardar_materias),
    path('eliminar-materias/<id>',views.eliminar_materias),
    path('editar-materias/<id>',views.editar_materias),
    path('procesar-info-materias',views.procesar_info_materias),

    #niveles
    path('listar-niveles',views.listar_niveles),
    path('crear-niveles',views.crear_niveles),
    path('guardar-niveles',views.guardar_niveles),
    path('eliminar-niveles/<id>',views.eliminar_niveles),
    path('editar-niveles/<id>',views.editar_niveles),
    path('procesar-info-niveles',views.procesar_info_niveles),

    
    # Asociar materias a tutores
    path('listar-tutores-materias', views.listar_tutores_materias),
    path('crear-tutores-materias', views.crear_tutores_materias),
    path('guardar-tutores-materias', views.guardar_tutores_materias),
    path('eliminar-tm/<id>',views.eliminar_tm),
    path('editar-tutores-materias/<id>', views.editar_tutores_materias),
    path('procesar-info-tutores-materias', views.procesar_info_tutores_materias),

]