from django.urls import path

from . import views

app_name = 'clientes'

urlpatterns = [
    path('', views.cliente_lista, name='lista'),
    path('crear/', views.cliente_crear, name='crear'),
    path('<int:pk>/editar/', views.cliente_editar, name='editar'),
    path('<int:pk>/eliminar/', views.cliente_eliminar, name='eliminar'),
]
