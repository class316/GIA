from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, Case, When, Value, CharField
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.views import rol_requerido
from auditoria.services import registrar_auditoria

from .forms import (
    EvidenciaOrdenForm,
    PARTES_SERVICIO,
    PRECIOS_SERVICIO,
    OrdenForm,
    OrdenHerramientaForm,
    OrdenRepuestoForm,
    SolicitudServicioForm,
    TrabajoMecanicoForm,
)
from .models import Orden


PRIORIDAD_ORDEN = {'urgente': 0, 'alta': 1, 'media': 2, 'baja': 3}


def liberar_herramientas(orden):
    for item in orden.herramientas_necesarias.select_related('herramienta'):
        herramienta = item.herramienta
        herramienta.estado = 'disponible'
        herramienta.mecanico_asignado = None
        herramienta.save(update_fields=['estado', 'mecanico_asignado'])


def puede_ver_orden(request, orden):
    if not request.user.is_authenticated:
        return False
    if request.user.rol == 'admin':
        return True
    if request.user.rol == 'cliente':
        cliente = getattr(request.user, 'cliente_taller', None)
        return bool(cliente and orden.cliente_id == cliente.id)
    if request.user.rol == 'mecanico':
        mecanico = getattr(request.user, 'mecanico_taller', None)
        return bool(mecanico and orden.mecanico_id == mecanico.id)
    return False


def redirigir_por_rol(request):
    if request.user.rol == 'admin':
        return redirect('admin_dashboard')
    if request.user.rol == 'cliente':
        return redirect('cliente_dashboard')
    if request.user.rol == 'mecanico':
        return redirect('mecanico_dashboard')
    return redirect('login')


@rol_requerido('admin')
def orden_lista(request):
    ordenes = Orden.objects.select_related('cliente', 'vehiculo', 'mecanico').prefetch_related('evidencias')
    ordenes = sorted(ordenes, key=lambda orden: (PRIORIDAD_ORDEN.get(orden.prioridad, 9), -orden.id))
    return render(request, 'ordenes/lista.html', {'ordenes': ordenes})


@rol_requerido('admin')
def orden_crear(request):
    if request.method == 'POST':
        form = OrdenForm(request.POST)
        if form.is_valid():
            orden = form.save(commit=False)
            orden.recalcular_costos(guardar=False)
            orden.save()
            registrar_auditoria(
                request,
                'creacion_orden',
                'Servicios y reparaciones',
                f'Se creo la orden #{orden.id} para {orden.cliente} - {orden.vehiculo}. Costo total: {orden.costo_total}.',
            )
            messages.success(request, 'Orden creada correctamente.')
            return redirect('ordenes:lista')
        messages.error(request, 'Revisa los campos marcados antes de continuar.')
    else:
        form = OrdenForm()
    return render(request, 'ordenes/crear.html', {'form': form, 'precios_servicio': PRECIOS_SERVICIO, 'partes_servicio': PARTES_SERVICIO})


@rol_requerido('admin')
def orden_editar(request, pk):
    orden = get_object_or_404(
        Orden.objects.select_related('cliente', 'vehiculo', 'mecanico').prefetch_related(
            'repuestos_usados__repuesto',
            'herramientas_necesarias__herramienta',
            'evidencias',
        ),
        pk=pk,
    )
    if request.method == 'POST':
        estado_anterior = orden.estado
        costo_anterior = orden.costo_total
        form = OrdenForm(request.POST, instance=orden)
        if form.is_valid():
            orden = form.save(commit=False)
            orden.recalcular_costos(guardar=False)
            orden.save()
            if orden.estado in ['finalizado', 'cancelado']:
                liberar_herramientas(orden)
            registrar_auditoria(
                request,
                'edicion_orden',
                'Servicios y reparaciones',
                f'Se actualizo la orden #{orden.id}. Estado: {estado_anterior} -> {orden.estado}. Costo: {costo_anterior} -> {orden.costo_total}.',
            )
            if estado_anterior != orden.estado:
                registrar_auditoria(
                    request,
                    'cambio_estado_orden',
                    'Servicios y reparaciones',
                    f'La orden #{orden.id} cambio de {estado_anterior} a {orden.estado}.',
                )
            if costo_anterior != orden.costo_total:
                registrar_auditoria(
                    request,
                    'cambio_costo',
                    'Servicios y reparaciones',
                    f'La orden #{orden.id} cambio costo de {costo_anterior} a {orden.costo_total}.',
                )
            messages.success(request, 'Informacion actualizada correctamente.')
            return redirect('ordenes:lista')
        messages.error(request, 'Revisa los campos marcados antes de continuar.')
    else:
        form = OrdenForm(instance=orden)
    return render(request, 'ordenes/editar.html', {'form': form, 'orden': orden, 'precios_servicio': PRECIOS_SERVICIO, 'partes_servicio': PARTES_SERVICIO})


@rol_requerido('admin')
def orden_eliminar(request, pk):
    orden = get_object_or_404(Orden, pk=pk)
    if request.method == 'POST':
        orden_eliminada = f'#{orden.id} - {orden.cliente} - {orden.vehiculo}'
        liberar_herramientas(orden)
        orden.delete()
        registrar_auditoria(
            request,
            'eliminacion_registro',
            'Servicios y reparaciones',
            f'Se elimino la orden {orden_eliminada}.',
        )
        messages.success(request, 'Registro eliminado correctamente.')
        return redirect('ordenes:lista')
    return render(request, 'ordenes/eliminar.html', {'orden': orden})


@rol_requerido('cliente')
def cliente_solicitar_servicio(request):
    cliente = getattr(request.user, 'cliente_taller', None)
    if not cliente:
        messages.error(request, 'Tu cuenta aun no tiene datos de cliente asociados.')
        return redirect('cliente_dashboard')

    if request.method == 'POST':
        form = SolicitudServicioForm(request.POST, cliente=cliente)
        if form.is_valid():
            orden = form.save(commit=False)
            orden.cliente = cliente
            orden.estado = 'pendiente'
            orden.costo_mano_obra = PRECIOS_SERVICIO.get(orden.tipo_servicio, 0)
            orden.costo_total = orden.costo_mano_obra
            orden.costo = orden.costo_total
            orden.save()
            registrar_auditoria(
                request,
                'creacion_orden',
                'Portal cliente',
                f'El cliente creo la solicitud de servicio #{orden.id} para {orden.vehiculo}.',
            )
            messages.success(request, 'Solicitud de servicio registrada correctamente.')
            return redirect('cliente_dashboard')
        messages.error(request, 'Revisa los campos marcados antes de continuar.')
    else:
        form = SolicitudServicioForm(cliente=cliente)

    return render(request, 'ordenes/solicitar_servicio.html', {'form': form, 'precios_servicio': PRECIOS_SERVICIO, 'partes_servicio': PARTES_SERVICIO})


@rol_requerido('mecanico')
def mecanico_solicitudes(request):
    mecanico = getattr(request.user, 'mecanico_taller', None)
    if not mecanico:
        messages.error(request, 'Tu cuenta aun no tiene datos de mecanico asociados.')
        return redirect('mecanico_dashboard')
    ordenes = Orden.objects.filter(estado='pendiente', mecanico__isnull=True).select_related('cliente', 'vehiculo')
    return render(request, 'ordenes/solicitudes_mecanico.html', {'ordenes': ordenes})


@rol_requerido('mecanico')
def mecanico_mis_trabajos(request):
    mecanico = getattr(request.user, 'mecanico_taller', None)
    if not mecanico:
        messages.error(request, 'Tu cuenta aun no tiene datos de mecanico asociados.')
        return redirect('mecanico_dashboard')
    ordenes = Orden.objects.filter(mecanico=mecanico).select_related('cliente', 'vehiculo').prefetch_related(
        'repuestos_usados__repuesto',
        'herramientas_necesarias__herramienta',
        'evidencias',
    )
    return render(request, 'ordenes/mis_trabajos.html', {'ordenes': ordenes})


@rol_requerido('mecanico')
def mecanico_aceptar(request, pk):
    mecanico = getattr(request.user, 'mecanico_taller', None)
    if not mecanico:
        messages.error(request, 'Tu cuenta aun no tiene datos de mecanico asociados.')
        return redirect('mecanico_dashboard')

    orden = get_object_or_404(Orden, pk=pk)
    if orden.mecanico_id:
        messages.error(request, 'Este servicio ya fue aceptado por otro mecanico.')
        return redirect('mecanico_solicitudes')
    if orden.estado != 'pendiente':
        messages.error(request, 'Solo puedes aceptar servicios pendientes.')
        return redirect('mecanico_solicitudes')

    orden.mecanico = mecanico
    orden.estado = 'en_proceso'
    orden.save(update_fields=['mecanico', 'estado'])
    registrar_auditoria(
        request,
        'cambio_estado_orden',
        'Estacion de mecanico',
        f'El mecanico {mecanico.nombre} acepto la orden #{orden.id}; estado pendiente -> en_proceso.',
    )
    messages.success(request, 'Servicio aceptado correctamente.')
    return redirect('mecanico_mis_trabajos')


@rol_requerido('mecanico')
def mecanico_actualizar(request, pk):
    mecanico = getattr(request.user, 'mecanico_taller', None)
    if not mecanico:
        messages.error(request, 'Tu cuenta aun no tiene datos de mecanico asociados.')
        return redirect('mecanico_dashboard')

    orden = get_object_or_404(
        Orden.objects.prefetch_related('repuestos_usados__repuesto', 'herramientas_necesarias__herramienta'),
        pk=pk,
    )
    if orden.mecanico_id != mecanico.id:
        messages.error(request, 'No puedes modificar un servicio asignado a otro mecanico.')
        return redirect('mecanico_mis_trabajos')

    if request.method == 'POST':
        estado_anterior = orden.estado
        costo_anterior = orden.costo_total
        form = TrabajoMecanicoForm(request.POST, instance=orden)
        if form.is_valid():
            orden_actualizada = form.save(commit=False)
            orden_actualizada.recalcular_costos(guardar=False)
            orden_actualizada.save()
            if orden_actualizada.estado in ['finalizado', 'cancelado']:
                liberar_herramientas(orden_actualizada)
            registrar_auditoria(
                request,
                'actualizacion_trabajo',
                'Estacion de mecanico',
                f'Se actualizo la orden #{orden_actualizada.id}. Estado: {estado_anterior} -> {orden_actualizada.estado}. Costo: {costo_anterior} -> {orden_actualizada.costo_total}.',
            )
            if estado_anterior != orden_actualizada.estado:
                registrar_auditoria(
                    request,
                    'cambio_estado_orden',
                    'Estacion de mecanico',
                    f'La orden #{orden_actualizada.id} cambio de {estado_anterior} a {orden_actualizada.estado}.',
                )
            if costo_anterior != orden_actualizada.costo_total:
                registrar_auditoria(
                    request,
                    'cambio_costo',
                    'Estacion de mecanico',
                    f'La orden #{orden_actualizada.id} cambio costo de {costo_anterior} a {orden_actualizada.costo_total}.',
                )
            messages.success(request, 'Estado actualizado correctamente.')
            return redirect('mecanico_mis_trabajos')
        messages.error(request, 'Revisa los campos marcados antes de continuar.')
    else:
        form = TrabajoMecanicoForm(instance=orden)
    return render(request, 'ordenes/actualizar_trabajo.html', {'form': form, 'orden': orden})


@rol_requerido('mecanico')
def orden_mecanico_estado(request, pk):
    return mecanico_actualizar(request, pk)


@rol_requerido('admin')
def orden_repuesto_agregar(request, pk):
    orden = get_object_or_404(Orden, pk=pk)

    if request.method == 'POST':
        form = OrdenRepuestoForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.orden = orden

            try:
                with transaction.atomic():
                    nuevo_stock = F('cantidad_disponible') - item.cantidad
                    actualizado = (
                        type(item.repuesto).objects
                        .filter(
                            pk=item.repuesto.pk,
                            cantidad_disponible__gte=item.cantidad,
                        )
                        .update(
                            cantidad_disponible=nuevo_stock,
                            estado=Case(
                                When(
                                    cantidad_disponible__lte=item.cantidad,
                                    then=Value('agotado'),
                                ),
                                When(
                                    cantidad_disponible__lte=item.cantidad + 3,
                                    then=Value('bajo_stock'),
                                ),
                                default=Value('disponible'),
                                output_field=CharField(),
                            ),
                        )
                    )

                    if not actualizado:
                        form.add_error(
                            'cantidad',
                            'No hay stock suficiente para esa cantidad.',
                        )
                        messages.error(request, 'No hay stock suficiente.')
                    else:
                        # Si guardar el detalle falla, la transaccion revierte
                        # tambien el descuento de stock y su estado.
                        item.save()

            except Exception:
                messages.error(
                    request,
                    'Ocurrio un error al agregar el repuesto. No se guardaron los cambios.',
                )
                return render(
                    request,
                    'ordenes/agregar_repuesto.html',
                    {'form': form, 'orden': orden},
                )

            if actualizado:
                item.repuesto.refresh_from_db()
                registrar_auditoria(
                    request,
                    'cambio_costo',
                    'Servicios y reparaciones',
                    f'Se agrego el repuesto {item.repuesto.nombre} x {item.cantidad} '
                    f'a la orden #{orden.id}. Subtotal: {item.subtotal}.',
                )
                messages.success(request, 'Repuesto asignado correctamente.')
                return redirect('ordenes:editar', pk=orden.pk)
        else:
            messages.error(
                request,
                'Revisa los campos marcados antes de continuar.',
            )
    else:
        form = OrdenRepuestoForm()

    return render(
        request,
        'ordenes/agregar_repuesto.html',
        {'form': form, 'orden': orden},
    )


@rol_requerido('admin')
def orden_herramienta_agregar(request, pk):
    orden = get_object_or_404(Orden, pk=pk)
    if request.method == 'POST':
        form = OrdenHerramientaForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.orden = orden
            item.herramienta.estado = 'en_uso'
            item.herramienta.mecanico_asignado = orden.mecanico
            item.herramienta.save(update_fields=['estado', 'mecanico_asignado'])
            item.save()
            registrar_auditoria(
                request,
                'asignacion_herramienta',
                'Servicios y reparaciones',
                f'Se asigno la herramienta {item.herramienta.nombre} a la orden #{orden.id}.',
            )
            messages.success(request, 'Herramienta asignada correctamente.')
            return redirect('ordenes:editar', pk=orden.pk)
        messages.error(request, 'La herramienta no esta disponible.')
    else:
        form = OrdenHerramientaForm()
    return render(request, 'ordenes/agregar_herramienta.html', {'form': form, 'orden': orden})


@rol_requerido('mecanico')
def evidencia_agregar(request, pk):
    mecanico = getattr(request.user, 'mecanico_taller', None)
    if not mecanico:
        messages.error(request, 'Tu cuenta aun no tiene datos de mecanico asociados.')
        return redirect('mecanico_dashboard')

    orden = get_object_or_404(Orden.objects.select_related('cliente', 'vehiculo', 'mecanico'), pk=pk)
    if orden.mecanico_id != mecanico.id:
        messages.error(request, 'No puedes agregar evidencia a un servicio asignado a otro mecanico.')
        return redirect('mecanico_mis_trabajos')

    if request.method == 'POST':
        form = EvidenciaOrdenForm(request.POST, request.FILES)
        if form.is_valid():
            evidencia = form.save(commit=False)
            evidencia.orden = orden
            evidencia.usuario = request.user
            evidencia.save()
            registrar_auditoria(
                request,
                'subida_evidencia',
                'Evidencia movil',
                f'Se subio evidencia {evidencia.get_tipo_display()} para la orden #{orden.id}.',
            )
            messages.success(request, 'Evidencia agregada correctamente.')
            return redirect('mecanico_mis_trabajos')
        messages.error(request, 'Revisa la imagen y los campos antes de continuar.')
    else:
        form = EvidenciaOrdenForm()

    return render(request, 'ordenes/agregar_evidencia.html', {'form': form, 'orden': orden})


@login_required
def evidencia_galeria(request, pk):
    orden = get_object_or_404(
        Orden.objects.select_related('cliente', 'vehiculo', 'mecanico').prefetch_related('evidencias'),
        pk=pk,
    )
    if not puede_ver_orden(request, orden):
        messages.error(request, 'No tienes permiso para ver esta evidencia.')
        return redirigir_por_rol(request)

    volver_url = 'ordenes:lista'
    if request.user.rol == 'cliente':
        volver_url = 'cliente_dashboard'
    elif request.user.rol == 'mecanico':
        volver_url = 'mecanico_mis_trabajos'

    return render(request, 'ordenes/evidencias.html', {'orden': orden, 'volver_url': volver_url})
