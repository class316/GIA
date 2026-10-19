from django.db import transaction
from django.utils import timezone

from .models import Auditoria


def obtener_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def registrar_auditoria(request, accion, modulo, descripcion):
    usuario = getattr(request, 'user', None)
    if not usuario or not usuario.is_authenticated:
        usuario = None

    usuario_identificador = ''
    if usuario:
        usuario_identificador = getattr(usuario, 'username', '') or str(usuario.pk)

    with transaction.atomic():
        ultimo = Auditoria.objects.select_for_update().order_by('-id').first()
        registro = Auditoria(
            usuario=usuario,
            usuario_identificador=usuario_identificador,
            accion=accion,
            modulo=modulo,
            descripcion=descripcion,
            ip=obtener_ip(request),
            hash_anterior=ultimo.hash_actual if ultimo else '',
        )
        registro.fecha_hora = timezone.now()
        registro.hash_actual = registro.calcular_hash()
        registro.save(force_insert=True)
        return registro


def verificar_integridad():
    registros = Auditoria.objects.order_by('id')
    hash_anterior = ''

    for registro in registros:
        if registro.hash_anterior != hash_anterior:
            return False, registro
        if registro.calcular_hash() != registro.hash_actual:
            return False, registro
        hash_anterior = registro.hash_actual

    return True, None
