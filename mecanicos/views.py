
import re
import unicodedata
import secrets

from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.models import Usuario
from usuarios.views import rol_requerido
from auditoria.services import registrar_auditoria

from .forms import MecanicoForm
from .models import Mecanico


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
    return limpio or 'mecanico'


def username_unico(nombre):
    base = username_base(nombre)
    username = base
    contador = 1

    while Usuario.objects.filter(username=username).exists():
        contador += 1
        username = f'{base}{contador}'

    return username


def crear_usuario_mecanico(mecanico):
    if mecanico.usuario:
        return mecanico.usuario, None

    if (
        mecanico.correo
        and Usuario.objects.filter(email__iexact=mecanico.correo).exists()
    ):
        raise ValueError(
            'Ya existe una cuenta de acceso con ese correo. '
            'Selecciónala en el formulario.'
        )

    first_name, last_name = separar_nombre(mecanico.nombre)
    password_temporal = secrets.token_urlsafe(16)

    usuario = Usuario.objects.create_user(
        username=username_unico(mecanico.nombre),
        password=password_temporal,
        email=mecanico.correo or '',
        first_name=first_name,
        last_name=last_name,
        rol='mecanico',
        is_active=True,
    )

    mecanico.usuario = usuario
    mecanico.save(update_fields=['usuario'])

    return usuario, password_temporal


@rol_requerido('admin')
def mecanico_lista(request):
    mecanicos = Mecanico.objects.select_related('usuario')
    return render(request, 'mecanicos/lista.html', {'mecanicos': mecanicos})


@rol_requerido('admin')
def mecanico_crear(request):
    if request.method == 'POST':
        form = MecanicoForm(request.POST)

        if form.is_valid():
            mecanico = form.save()

            if mecanico.usuario:
                registrar_auditoria(
                    request,
                    'creacion_mecanico',
                    'Equipo mecanico',
                    (
                        f'Se creo el mecanico {mecanico.nombre} vinculado '
                        f'a la cuenta {mecanico.usuario.username}.'
                    ),
                )
                messages.success(
                    request,
                    'Registro creado correctamente y vinculado '
                    'a la cuenta seleccionada.',
                )
                return redirect('mecanicos:lista')

            try:
                usuario, password_temporal = crear_usuario_mecanico(mecanico)

            except ValueError as exc:
                mecanico.delete()
                form.add_error('correo', str(exc))
                messages.error(
                    request,
                    'Revisa los campos marcados antes de continuar.',
                )

            else:
                registrar_auditoria(
                    request,
                    'creacion_mecanico',
                    'Equipo mecanico',
                    (
                        f'Se creo el mecanico {mecanico.nombre} y la cuenta '
                        f'temporal {usuario.username}.'
                    ),
                )

                messages.success(
                    request,
                    (
                        'Mecánico registrado correctamente. '
                        'Se creó una cuenta de acceso temporal. '
                        f'Usuario: {usuario.username} / '
                        f'Contraseña temporal: {password_temporal}'
                    ),
                )
                return redirect('mecanicos:lista')

        else:
            messages.error(
                request,
                'Revisa los campos marcados antes de continuar.',
            )

    else:
        form = MecanicoForm()

    return render(request, 'mecanicos/crear.html', {'form': form})


@rol_requerido('admin')
def mecanico_editar(request, pk):
    mecanico = get_object_or_404(Mecanico, pk=pk)

    if request.method == 'POST':
        form = MecanicoForm(request.POST, instance=mecanico)

        if form.is_valid():
            mecanico = form.save()

            registrar_auditoria(
                request,
                'edicion_mecanico',
                'Equipo mecanico',
                f'Se actualizo la informacion del mecanico {mecanico.nombre}.',
            )

            messages.success(
                request,
                'Información actualizada correctamente.',
            )
            return redirect('mecanicos:lista')

        messages.error(
            request,
            'Revisa los campos marcados antes de continuar.',
        )

    else:
        form = MecanicoForm(instance=mecanico)

    return render(
        request,
        'mecanicos/editar.html',
        {'form': form, 'mecanico': mecanico},
    )


@rol_requerido('admin')
def mecanico_eliminar(request, pk):
    mecanico = get_object_or_404(Mecanico, pk=pk)

    if request.method == 'POST':
        nombre_mecanico = mecanico.nombre
        usuario = mecanico.usuario

        try:
            if usuario:
                usuario.delete()
            else:
                mecanico.delete()

        except ProtectedError:
            messages.error(
                request,
                'No se puede eliminar porque tiene información asociada.',
            )
            return redirect('mecanicos:lista')

        registrar_auditoria(
            request,
            'eliminacion_registro',
            'Equipo mecanico',
            f'Se elimino el mecanico {nombre_mecanico}.',
        )

        messages.success(request, 'Registro eliminado correctamente.')

        if usuario:
            messages.info(request, 'Cuenta eliminada correctamente.')

        return redirect('mecanicos:lista')

    return render(
        request,
        'mecanicos/eliminar.html',
        {'mecanico': mecanico},
    )
