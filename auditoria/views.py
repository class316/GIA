from django.contrib import messages
from django.shortcuts import render

from usuarios.views import rol_requerido

from .models import Auditoria
from .services import registrar_auditoria, verificar_integridad


@rol_requerido('admin')
def lista(request):
    estado_integridad = None
    registro_alterado = None

    if request.method == 'POST':
        es_valida, registro_alterado = verificar_integridad()
        estado_integridad = 'valida' if es_valida else 'alterada'
        if es_valida:
            messages.success(request, 'Cadena valida. No se detectaron alteraciones.')
        else:
            messages.error(request, 'Cadena alterada. Revisa el registro marcado.')
        registrar_auditoria(
            request,
            'verificacion_integridad',
            'Auditoria de seguridad',
            'El administrador verifico la integridad de la cadena de auditoria.',
        )

    auditorias = Auditoria.objects.select_related('usuario').order_by('-id')[:250]
    return render(
        request,
        'auditoria/lista.html',
        {
            'auditorias': auditorias,
            'estado_integridad': estado_integridad,
            'registro_alterado': registro_alterado,
        },
    )
