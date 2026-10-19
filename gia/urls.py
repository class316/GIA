"""
URL configuration for gia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import TemplateView
from usuarios.views import (
    admin_dashboard,
    cliente_dashboard,
    login_view,
    logout_view,
    mecanico_dashboard,
)
from ordenes import views as ordenes_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'service-worker.js',
        TemplateView.as_view(template_name='pwa/service-worker.js', content_type='application/javascript'),
        name='service_worker',
    ),

    # LOGIN
    path('', login_view, name='login'),

    # LOGOUT
    path('logout/', logout_view, name='logout'),

    # DASHBOARDS
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('cliente-dashboard/', cliente_dashboard, name='cliente_dashboard'),
    path('mecanico-dashboard/', mecanico_dashboard, name='mecanico_dashboard'),

    # USUARIOS
    path('usuarios/', include('usuarios.urls')),
    path('clientes/', include('clientes.urls')),
    path('mecanicos/', include('mecanicos.urls')),
    path('vehiculos/', include('vehiculos.urls')),
    path('ordenes/', include('ordenes.urls')),
    path('repuestos/', include('repuestos.urls')),
    path('herramientas/', include('herramientas.urls')),
    path('cotizaciones/', include('cotizaciones.urls')),
    path('gastos/', include('gastos.urls')),
    path('auditoria/', include('auditoria.urls')),
    path('cliente/solicitar-servicio/', ordenes_views.cliente_solicitar_servicio, name='cliente_solicitar_servicio'),
    path('mecanico/solicitudes/', ordenes_views.mecanico_solicitudes, name='mecanico_solicitudes'),
    path('mecanico/mis-trabajos/', ordenes_views.mecanico_mis_trabajos, name='mecanico_mis_trabajos'),
    path('mecanico/aceptar/<int:pk>/', ordenes_views.mecanico_aceptar, name='mecanico_aceptar'),
    path('mecanico/actualizar/<int:pk>/', ordenes_views.mecanico_actualizar, name='mecanico_actualizar'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
