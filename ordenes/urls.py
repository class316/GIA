from django.urls import path

from . import views

app_name = 'ordenes'

urlpatterns = [
    path('', views.orden_lista, name='lista'),
    path('crear/', views.orden_crear, name='crear'),
    path('<int:pk>/editar/', views.orden_editar, name='editar'),
    path('<int:pk>/eliminar/', views.orden_eliminar, name='eliminar'),
    path('<int:pk>/estado/', views.orden_mecanico_estado, name='estado_mecanico'),
    path('<int:pk>/agregar-repuesto/', views.orden_repuesto_agregar, name='agregar_repuesto'),
    path('<int:pk>/agregar-herramienta/', views.orden_herramienta_agregar, name='agregar_herramienta'),
    path('<int:pk>/evidencias/', views.evidencia_galeria, name='evidencias'),
    path('<int:pk>/agregar-evidencia/', views.evidencia_agregar, name='agregar_evidencia'),
]
