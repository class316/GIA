from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from ordenes.models import Orden
from usuarios.views import rol_requerido
from auditoria.services import registrar_auditoria

from .forms import CotizacionAdminForm, CotizacionClienteForm, CotizacionMecanicoForm
from .models import Cotizacion


@rol_requerido('admin')
def lista(request):
    cotizaciones = Cotizacion.objects.select_related('cliente', 'vehiculo', 'mecanico_revisor', 'orden_generada')
    return render(request, 'cotizaciones/lista.html', {'cotizaciones': cotizaciones})


@rol_requerido('cliente')
def cliente_lista(request):
    cliente = getattr(request.user, 'cliente_taller', None)
    cotizaciones = Cotizacion.objects.none()
    if cliente:
        cotizaciones = cliente.cotizaciones.select_related('vehiculo')
    return render(request, 'cotizaciones/cliente_lista.html', {'cliente': cliente, 'cotizaciones': cotizaciones})


@rol_requerido('cliente')
def solicitar(request):
    cliente = getattr(request.user, 'cliente_taller', None)
    if not cliente:
        messages.error(request, 'Tu cuenta aun no tiene datos de cliente asociados.')
        return redirect('cliente_dashboard')

    if request.method == 'POST':
        form = CotizacionClienteForm(request.POST, cliente=cliente)
        if form.is_valid():
            cotizacion = form.save(commit=False)
            cotizacion.cliente = cliente
            cotizacion.save()
            registrar_auditoria(
                request,
                'creacion_registro',
                'Cotizaciones',
                f'El cliente {cliente.nombre} solicito la cotizacion #{cotizacion.id}.',
            )
            messages.success(request, 'Cotizacion enviada correctamente.')
            return redirect('cotizaciones:cliente_lista')
        messages.error(request, 'Revisa los campos marcados antes de continuar.')
    else:
        form = CotizacionClienteForm(cliente=cliente)
    return render(request, 'cotizaciones/solicitar.html', {'form': form})


@rol_requerido('admin')
def revisar(request, pk):
    cotizacion = get_object_or_404(Cotizacion.objects.select_related('cliente', 'vehiculo', 'mecanico_revisor'), pk=pk)
    if request.method == 'POST':
        form = CotizacionAdminForm(request.POST, instance=cotizacion)
        if form.is_valid():
            cotizacion = form.save()
            registrar_auditoria(
                request,
                'edicion_registro',
                'Cotizaciones',
                f'Se reviso la cotizacion #{cotizacion.id}. Estado actual: {cotizacion.estado}.',
            )
            messages.success(request, 'Cotizacion actualizada correctamente.')
            return redirect('cotizaciones:lista')
        messages.error(request, 'Revisa los campos marcados antes de continuar.')
    else:
        form = CotizacionAdminForm(instance=cotizacion)
    return render(request, 'cotizaciones/revisar.html', {'form': form, 'cotizacion': cotizacion})


@rol_requerido('mecanico')
def mecanico_lista(request):
    cotizaciones = Cotizacion.objects.select_related('cliente', 'vehiculo', 'mecanico_revisor').filter(
        estado__in=['pendiente', 'revisada']
    )
    return render(request, 'cotizaciones/mecanico_lista.html', {'cotizaciones': cotizaciones})


@rol_requerido('mecanico')
def mecanico_sugerir(request, pk):
    mecanico = getattr(request.user, 'mecanico_taller', None)
    if not mecanico:
        messages.error(request, 'Tu cuenta aun no tiene datos de mecanico asociados.')
        return redirect('mecanico_dashboard')

    cotizacion = get_object_or_404(Cotizacion.objects.select_related('cliente', 'vehiculo'), pk=pk)
    if request.method == 'POST':
        form = CotizacionMecanicoForm(request.POST, instance=cotizacion)
        if form.is_valid():
            cotizacion = form.save(commit=False)
            cotizacion.mecanico_revisor = mecanico
            cotizacion.estado = 'revisada'
            cotizacion.save()
            form.save_m2m()
            registrar_auditoria(
                request,
                'edicion_registro',
                'Cotizaciones',
                f'El mecanico {mecanico.nombre} agrego sugerencia tecnica a la cotizacion #{cotizacion.id}.',
            )
            messages.success(request, 'Sugerencia tecnica guardada correctamente.')
            return redirect('cotizaciones:mecanico_lista')
        messages.error(request, 'Revisa los campos marcados antes de continuar.')
    else:
        form = CotizacionMecanicoForm(instance=cotizacion)
    return render(request, 'cotizaciones/mecanico_sugerir.html', {'form': form, 'cotizacion': cotizacion})


@rol_requerido('admin')
def convertir_orden(request, pk):
    with transaction.atomic():
        cotizacion = get_object_or_404(
            Cotizacion.objects.select_for_update().select_related('orden_generada'),
            pk=pk,
        )

        if cotizacion.orden_generada_id:
            registrar_auditoria(
                request,
                'conversion_bloqueada',
                'Cotizaciones',
                f'Se intento convertir de nuevo la cotizacion #{cotizacion.id}, ya vinculada a la orden #{cotizacion.orden_generada_id}.',
            )
            messages.warning(request, 'Esta cotización ya fue convertida en una orden de trabajo.')
            return redirect('ordenes:editar', pk=cotizacion.orden_generada_id)

        if cotizacion.estado != 'aprobada':
            messages.error(request, 'Solo una cotización aprobada puede convertirse en orden.')
            return redirect('cotizaciones:lista')

        orden = Orden.objects.create(
            cliente=cotizacion.cliente,
            vehiculo=cotizacion.vehiculo,
            tipo_servicio=(cotizacion.servicios_catalogo[0] if cotizacion.servicios_catalogo else 'revision_general'),
            descripcion=cotizacion.servicios_sugeridos,
            falla_reportada=cotizacion.descripcion_falla,
            diagnostico=cotizacion.diagnostico_mecanico,
            trabajo_a_realizar=cotizacion.servicios_sugeridos,
            prioridad=cotizacion.prioridad,
            estado='pendiente',
            costo_mano_obra=cotizacion.costo_estimado,
            costo=cotizacion.costo_estimado,
            costo_total=cotizacion.costo_estimado,
        )
        cotizacion.orden_generada = orden
        cotizacion.save(update_fields=['orden_generada'])

        registrar_auditoria(
            request,
            'creacion_orden',
            'Cotizaciones',
            f'Se convirtio la cotizacion #{cotizacion.id} en la orden #{orden.id}.',
        )

    messages.success(request, 'Orden de trabajo creada correctamente desde la cotización.')
    return redirect('ordenes:editar', pk=orden.pk)
