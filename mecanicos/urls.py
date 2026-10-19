from django.urls import path

from . import views

app_name = 'mecanicos'

urlpatterns = [
    path('', views.mecanico_lista, name='lista'),
    path('crear/', views.mecanico_crear, name='crear'),
    path('<int:pk>/editar/', views.mecanico_editar, name='editar'),
    path('<int:pk>/eliminar/', views.mecanico_eliminar, name='eliminar'),
]
