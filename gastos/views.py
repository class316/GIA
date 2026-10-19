from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.views import rol_requerido
from auditoria.services import registrar_auditoria

from .forms import GastoForm
from .models import Gasto


@rol_requerido('admin')
def lista(request):
    gastos = Gasto.objects.all()
    return render(request, 'gastos/lista.html', {'gastos': gastos})


@rol_requerido('admin')
def crear(request):
    if request.method == 'POST':
        form = GastoForm(request.POST)
        if form.is_valid():
            gasto = form.save()
            registrar_auditoria(
                request,
                'creacion_registro',
                'Gastos',
                f'Se creo el gasto {gasto.concepto} por valor {gasto.valor}.',
            )
            messages.success(request, 'Gasto registrado correctamente.')
            return redirect('gastos:lista')
        messages.error(request, 'Revisa los campos marcados antes de continuar.')
    else:
        form = GastoForm()
    return render(request, 'gastos/crear.html', {'form': form})


@rol_requerido('admin')
def editar(request, pk):
    gasto = get_object_or_404(Gasto, pk=pk)
    if request.method == 'POST':
        form = GastoForm(request.POST, instance=gasto)
        if form.is_valid():
            gasto = form.save()
            registrar_auditoria(
                request,
                'edicion_registro',
                'Gastos',
                f'Se actualizo el gasto {gasto.concepto} por valor {gasto.valor}.',
            )
            messages.success(request, 'Informacion actualizada correctamente.')
            return redirect('gastos:lista')
        messages.error(request, 'Revisa los campos marcados antes de continuar.')
    else:
        form = GastoForm(instance=gasto)
    return render(request, 'gastos/editar.html', {'form': form, 'gasto': gasto})


@rol_requerido('admin')
def eliminar(request, pk):
    gasto = get_object_or_404(Gasto, pk=pk)
    if request.method == 'POST':
        gasto_eliminado = f'{gasto.concepto} ({gasto.valor})'
        gasto.delete()
        registrar_auditoria(
            request,
            'eliminacion_registro',
            'Gastos',
            f'Se elimino el gasto {gasto_eliminado}.',
        )
        messages.success(request, 'Registro eliminado correctamente.')
        return redirect('gastos:lista')
    return render(request, 'gastos/eliminar.html', {'gasto': gasto})
