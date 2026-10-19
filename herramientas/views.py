from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.views import rol_requerido
from auditoria.services import registrar_auditoria

from .forms import HerramientaForm
from .models import Herramienta


@rol_requerido('admin')
def lista(request):
    herramientas = Herramienta.objects.select_related('mecanico_asignado')
    return render(request, 'herramientas/lista.html', {'herramientas': herramientas})


@rol_requerido('admin')
def crear(request):
    if request.method == 'POST':
        form = HerramientaForm(request.POST)
        if form.is_valid():
            herramienta = form.save()
            registrar_auditoria(
                request,
                'creacion_registro',
                'Herramientas y equipos',
                f'Se creo la herramienta {herramienta.nombre} con codigo {herramienta.codigo_interno}.',
            )
            messages.success(request, 'Herramienta registrada correctamente.')
            return redirect('herramientas:lista')
        messages.error(request, 'Revisa los campos marcados antes de continuar.')
    else:
        form = HerramientaForm()
    return render(request, 'herramientas/crear.html', {'form': form})


@rol_requerido('admin')
def editar(request, pk):
    herramienta = get_object_or_404(Herramienta, pk=pk)
    if request.method == 'POST':
        form = HerramientaForm(request.POST, instance=herramienta)
        if form.is_valid():
            herramienta = form.save()
            registrar_auditoria(
                request,
                'edicion_registro',
                'Herramientas y equipos',
                f'Se actualizo la herramienta {herramienta.nombre}. Estado actual: {herramienta.estado}.',
            )
            messages.success(request, 'Informacion actualizada correctamente.')
            return redirect('herramientas:lista')
        messages.error(request, 'Revisa los campos marcados antes de continuar.')
    else:
        form = HerramientaForm(instance=herramienta)
    return render(request, 'herramientas/editar.html', {'form': form, 'herramienta': herramienta})


@rol_requerido('admin')
def eliminar(request, pk):
    herramienta = get_object_or_404(Herramienta, pk=pk)
    if request.method == 'POST':
        if herramienta.ordenes_asignadas.exists():
            messages.error(request, 'No se puede eliminar porque tiene informacion asociada.')
            return redirect('herramientas:lista')
        herramienta_eliminada = f'{herramienta.nombre} ({herramienta.codigo_interno})'
        herramienta.delete()
        registrar_auditoria(
            request,
            'eliminacion_registro',
            'Herramientas y equipos',
            f'Se elimino la herramienta {herramienta_eliminada}.',
        )
        messages.success(request, 'Registro eliminado correctamente.')
        return redirect('herramientas:lista')
    return render(request, 'herramientas/eliminar.html', {'herramienta': herramienta})
