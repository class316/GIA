from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.views import rol_requerido
from auditoria.services import registrar_auditoria

from .forms import RepuestoForm
from .models import Repuesto


@rol_requerido('admin')
def lista(request):
    repuestos = Repuesto.objects.all()
    return render(request, 'repuestos/lista.html', {'repuestos': repuestos})


@rol_requerido('admin')
def crear(request):
    if request.method == 'POST':
        form = RepuestoForm(request.POST)
        if form.is_valid():
            repuesto = form.save()
            registrar_auditoria(
                request,
                'creacion_registro',
                'Repuestos',
                f'Se creo el repuesto {repuesto.nombre} con referencia {repuesto.referencia}.',
            )
            messages.success(request, 'Repuesto registrado correctamente.')
            return redirect('repuestos:lista')
        messages.error(request, 'Revisa los campos marcados antes de continuar.')
    else:
        form = RepuestoForm()
    return render(request, 'repuestos/crear.html', {'form': form})


@rol_requerido('admin')
def editar(request, pk):
    repuesto = get_object_or_404(Repuesto, pk=pk)
    if request.method == 'POST':
        form = RepuestoForm(request.POST, instance=repuesto)
        if form.is_valid():
            repuesto = form.save()
            registrar_auditoria(
                request,
                'edicion_registro',
                'Repuestos',
                f'Se actualizo el repuesto {repuesto.nombre} con referencia {repuesto.referencia}.',
            )
            messages.success(request, 'Informacion actualizada correctamente.')
            return redirect('repuestos:lista')
        messages.error(request, 'Revisa los campos marcados antes de continuar.')
    else:
        form = RepuestoForm(instance=repuesto)
    return render(request, 'repuestos/editar.html', {'form': form, 'repuesto': repuesto})


@rol_requerido('admin')
def eliminar(request, pk):
    repuesto = get_object_or_404(Repuesto, pk=pk)
    if request.method == 'POST':
        if repuesto.usos_en_ordenes.exists():
            messages.error(request, 'No se puede eliminar porque tiene informacion asociada.')
            return redirect('repuestos:lista')
        repuesto_eliminado = f'{repuesto.nombre} ({repuesto.referencia})'
        repuesto.delete()
        registrar_auditoria(
            request,
            'eliminacion_registro',
            'Repuestos',
            f'Se elimino el repuesto {repuesto_eliminado}.',
        )
        messages.success(request, 'Registro eliminado correctamente.')
        return redirect('repuestos:lista')
    return render(request, 'repuestos/eliminar.html', {'repuesto': repuesto})
