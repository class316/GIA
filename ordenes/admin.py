from django.contrib import admin

from .models import Orden


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'vehiculo', 'mecanico', 'tipo_servicio', 'estado', 'costo', 'fecha_ingreso')
    list_filter = ('tipo_servicio', 'estado', 'fecha_ingreso')
    search_fields = ('cliente__nombre', 'vehiculo__placa', 'mecanico__nombre')
