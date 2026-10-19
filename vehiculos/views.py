from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.views import rol_requerido
from auditoria.services import registrar_auditoria

from .forms import VehiculoForm
from .models import Vehiculo


@rol_requerido('admin')
def vehiculo_lista(request):
    vehiculos = Vehiculo.objects.select_related('cliente')
    return render(request, 'vehiculos/lista.html', {'vehiculos': vehiculos})


@rol_requerido('admin')
def vehiculo_crear(request):
    if request.method == 'POST':
        form = VehiculoForm(request.POST)
        if form.is_valid():
            vehiculo = form.save()
            registrar_auditoria(
                request,
                'creacion_vehiculo',
                'Vehiculos registrados',
                f'Se creo el vehiculo {vehiculo.placa} para el cliente {vehiculo.cliente}.',
            )
            messages.success(request, 'Vehículo registrado correctamente.')
            return redirect('vehiculos:lista')
        messages.error(request, 'Revisa los campos marcados antes de continuar')
    else:
        form = VehiculoForm()
    return render(request, 'vehiculos/crear.html', {'form': form})


@rol_requerido('admin')
def vehiculo_editar(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    if request.method == 'POST':
        form = VehiculoForm(request.POST, instance=vehiculo)
        if form.is_valid():
            vehiculo = form.save()
            registrar_auditoria(
                request,
                'edicion_vehiculo',
                'Vehiculos registrados',
                f'Se actualizo el vehiculo {vehiculo.placa}.',
            )
            messages.success(request, 'Información actualizada correctamente')
            return redirect('vehiculos:lista')
        messages.error(request, 'Revisa los campos marcados antes de continuar')
    else:
        form = VehiculoForm(instance=vehiculo)
    return render(request, 'vehiculos/editar.html', {'form': form, 'vehiculo': vehiculo})


@rol_requerido('admin')
def vehiculo_eliminar(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    if request.method == 'POST':
        vehiculo_eliminado = vehiculo.placa
        vehiculo.delete()
        registrar_auditoria(
            request,
            'eliminacion_registro',
            'Vehiculos registrados',
            f'Se elimino el vehiculo {vehiculo_eliminado}.',
        )
        messages.success(request, 'Registro eliminado correctamente')
        return redirect('vehiculos:lista')
    return render(request, 'vehiculos/eliminar.html', {'vehiculo': vehiculo})
