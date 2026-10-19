
import re
import unicodedata
import secrets

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.models import Usuario
from usuarios.views import rol_requerido
from auditoria.services import registrar_auditoria

from .forms import ClienteForm
from .models import Cliente


def separar_nombre(nombre):
    partes = nombre.split()
    if not partes:
        return '', ''
    return partes[0], ' '.join(partes[1:])


def username_base(nombre):
    limpio = (
        unicodedata.normalize('NFKD', nombre)
        .encode('ascii', 'ignore')
        .decode('ascii')
    )
    limpio = re.sub(r'[^a-zA-Z0-9]+', '', limpio).lower()
    return limpio or 'cliente'


def username_unico(nombre):
    base = username_base(nombre)
    username = base
    contador = 1

    while Usuario.objects.filter(username=username).exists():
        contador += 1
        username = f'{base}{contador}'

    return username


def crear_usuario_cliente(cliente):
    if cliente.usuario:
        return cliente.usuario, None

    if (
        cliente.correo
        and Usuario.objects.filter(email__iexact=cliente.correo).exists()
    ):
        raise ValueError(
            'Ya existe una cuenta de acceso con ese correo. '
            'Selecciónala en el formulario.'
        )

    first_name, last_name = separar_nombre(cliente.nombre)
    password_temporal = secrets.token_urlsafe(16)

    usuario = Usuario.objects.create_user(
        username=username_unico(cliente.nombre),
        password=password_temporal,
        email=cliente.correo or '',
        first_name=first_name,
        last_name=last_name,
        rol='cliente',
        is_active=True,
    )

    cliente.usuario = usuario
    cliente.save(update_fields=['usuario'])

    return usuario, password_temporal


@rol_requerido('admin')
def cliente_lista(request):
    clientes = Cliente.objects.select_related('usuario')
    return render(request, 'clientes/lista.html', {'clientes': clientes})


@rol_requerido('admin')
def cliente_crear(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)

        if form.is_valid():
            cliente = form.save()

            if cliente.usuario:
                registrar_auditoria(
                    request,
                    'creacion_cliente',
                    'Clientes del taller',
                    (
                        f'Se creo el cliente {cliente.nombre} vinculado '
                        f'a la cuenta {cliente.usuario.username}.'
                    ),
                )

                messages.success(
                    request,
                    'Registro creado correctamente y vinculado '
                    'a la cuenta seleccionada.',
                )
                return redirect('clientes:lista')

            try:
                usuario, password_temporal = crear_usuario_cliente(cliente)

            except ValueError as exc:
                cliente.delete()
                form.add_error('correo', str(exc))
                messages.error(
                    request,
                    'Revisa los campos marcados antes de continuar.',
                )

            else:
                registrar_auditoria(
                    request,
                    'creacion_cliente',
                    'Clientes del taller',
                    (
                        f'Se creo el cliente {cliente.nombre} y la cuenta '
                        f'temporal {usuario.username}.'
                    ),
                )

                messages.success(
                    request,
                    (
                        'Cliente registrado correctamente. '
                        'Se creó una cuenta de acceso temporal. '
                        f'Usuario: {usuario.username} / '
                        f'Contraseña temporal: {password_temporal}'
                    ),
                )

                return redirect('clientes:lista')

        else:
            messages.error(
                request,
                'Revisa los campos marcados antes de continuar.',
            )

    else:
        form = ClienteForm()

    return render(request, 'clientes/crear.html', {'form': form})


@rol_requerido('admin')
def cliente_editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)

        if form.is_valid():
            cliente = form.save()

            registrar_auditoria(
                request,
                'edicion_cliente',
                'Clientes del taller',
                (
                    f'Se actualizo la informacion del cliente '
                    f'{cliente.nombre}.'
                ),
            )

            messages.success(
                request,
                'Información actualizada correctamente.',
            )
            return redirect('clientes:lista')

        messages.error(
            request,
            'Revisa los campos marcados antes de continuar.',
        )

    else:
        form = ClienteForm(instance=cliente)

    return render(
        request,
        'clientes/editar.html',
        {'form': form, 'cliente': cliente},
    )


@rol_requerido('admin')
def cliente_eliminar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST':
        if cliente.vehiculos.exists() or cliente.ordenes.exists():
            messages.error(
                request,
                'No se puede eliminar porque tiene información asociada.',
            )
            return redirect('clientes:lista')

        usuario = cliente.usuario
        cliente_eliminado = cliente.nombre

        if usuario:
            usuario.delete()
        else:
            cliente.delete()

        registrar_auditoria(
            request,
            'eliminacion_registro',
            'Clientes del taller',
            f'Se elimino el cliente {cliente_eliminado}.',
        )

        messages.success(
            request,
            'Registro eliminado correctamente.',
        )

        if usuario:
            messages.info(request, 'Cuenta eliminada correctamente.')

        return redirect('clientes:lista')

    return render(
        request,
        'clientes/eliminar.html',
        {'cliente': cliente},
    )
