from django.urls import path
from . import views

urlpatterns = [
    # Páginas públicas
    path('', views.inicio, name='inicio'),
    path('acerca-de/', views.acerca_de, name='acerca_de'),
    path('contacto/', views.contacto, name='contacto'),
    
    # Autenticación
    path('logout/', views.cerrar_sesion, name='logout'),
    
    # Gestión de niños (requiere login)
    path('ninos/', views.lista_ninos, name='lista_ninos'),
    path('ninos/registrar/', views.registrar_nino, name='registrar_nino'),
    path('ninos/<int:pk>/', views.detalle_nino, name='detalle_nino'),
    path('ninos/<int:pk>/editar/', views.editar_nino, name='editar_nino'),
    path('ninos/<int:pk>/eliminar/', views.eliminar_nino, name='eliminar_nino'),


# Gestión de responsables autorizados (requiere login)
    path('ninos/<int:nino_pk>/responsables/', views.lista_responsables, name='lista_responsables'),
    path('ninos/<int:nino_pk>/responsables/registrar/', views.registrar_responsable, name='registrar_responsable'),
    path('responsables/<int:pk>/', views.detalle_responsable, name='detalle_responsable'),
    path('responsables/<int:pk>/editar/', views.editar_responsable, name='editar_responsable'),
    path('responsables/<int:pk>/eliminar/', views.eliminar_responsable, name='eliminar_responsable'),

]