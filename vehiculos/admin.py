from django.contrib import admin

from .models import Vehiculo


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('placa', 'marca', 'modelo', 'anio', 'cliente')
    search_fields = ('placa', 'marca', 'modelo', 'cliente__nombre')
