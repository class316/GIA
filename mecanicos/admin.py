from django.contrib import admin

from .models import Mecanico


@admin.register(Mecanico)
class MecanicoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'correo', 'especialidad', 'estado')
    list_filter = ('estado',)
    search_fields = ('nombre', 'correo', 'especialidad')
