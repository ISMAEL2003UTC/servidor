from django.urls import path
from . import views
urlpatterns = [
    path('', views.home),
    path('listar-usuarios',views.listar_usuarios),
    path('crear-usuarios',views.crear_usuarios),
    path('guardar-usuarios',views.guardar_usuarios),
    #path('eliminar-usuarios/<id>',views.eliminar_usuarios),
    #path('editar-usuarios/<id>',views.editar_usuarios),
    #path('procesar-info-usuarios',views.procesar_info_usuarios)
]