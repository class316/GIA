from django.contrib import admin

from .models import Auditoria


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('fecha_hora', 'usuario_identificador', 'accion', 'modulo', 'ip')
    search_fields = ('usuario_identificador', 'accion', 'modulo', 'descripcion', 'ip')
    list_filter = ('modulo', 'accion', 'fecha_hora')
    readonly_fields = (
        'usuario',
        'usuario_identificador',
        'accion',
        'modulo',
        'descripcion',
        'fecha_hora',
        'ip',
        'hash_anterior',
        'hash_actual',
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
