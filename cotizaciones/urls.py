from django.urls import path

from . import views

app_name = 'cotizaciones'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('mis-cotizaciones/', views.cliente_lista, name='cliente_lista'),
    path('solicitar/', views.solicitar, name='solicitar'),
    path('mecanico/', views.mecanico_lista, name='mecanico_lista'),
    path('mecanico/<int:pk>/sugerir/', views.mecanico_sugerir, name='mecanico_sugerir'),
    path('<int:pk>/revisar/', views.revisar, name='revisar'),
    path('<int:pk>/convertir-orden/', views.convertir_orden, name='convertir_orden'),
]
