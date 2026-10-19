from functools import wraps
import re

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import UsuarioEditarForm, UsuarioForm
from .models import Usuario
from auditoria.services import registrar_auditoria


LOGIN_MAX_ATTEMPTS = 5
LOGIN_LOCK_SECONDS = 300
USERNAME_RE = re.compile(r'^[\w.@+-]+$')


def formato_pesos_colombianos(valor):
    valor_entero = int(valor or 0)
    if valor_entero <= 0:
        return '$0 COP'
    return f'${valor_entero:,}'.replace(',', '.') + ' COP'


def nombre_para_perfil(usuario):
    nombre = f'{usuario.first_name} {usuario.last_name}'.strip()
    return nombre or usuario.username


def correo_disponible(modelo, usuario):
    correo = (usuario.email or '').strip().lower()
    if not correo:
        return None
    if modelo.objects.filter(correo__iexact=correo).exclude(usuario=usuario).exists():
        return None
    return correo


def asegurar_perfil_por_rol(usuario):
    from clientes.models import Cliente
    from mecanicos.models import Mecanico

    if usuario.rol == 'cliente':
        if hasattr(usuario, 'mecanico_taller'):
            usuario.mecanico_taller.usuario = None
            usuario.mecanico_taller.save(update_fields=['usuario'])
        Cliente.objects.get_or_create(
            usuario=usuario,
            defaults={
                'nombre': nombre_para_perfil(usuario),
                'telefono': '',
                'correo': correo_disponible(Cliente, usuario),
                'direccion': '',
            },
        )
        return 'cliente'

    if usuario.rol == 'mecanico':
        if hasattr(usuario, 'cliente_taller'):
            usuario.cliente_taller.usuario = None
            usuario.cliente_taller.save(update_fields=['usuario'])
        Mecanico.objects.get_or_create(
            usuario=usuario,
            defaults={
                'nombre': nombre_para_perfil(usuario),
                'telefono': '',
                'correo': correo_disponible(Mecanico, usuario),
                'especialidad': 'Sin asignar',
                'estado': 'activo',
            },
        )
        return 'mecanico'

    if hasattr(usuario, 'cliente_taller'):
        usuario.cliente_taller.usuario = None
        usuario.cliente_taller.save(update_fields=['usuario'])
    if hasattr(usuario, 'mecanico_taller'):
        usuario.mecanico_taller.usuario = None
        usuario.mecanico_taller.save(update_fields=['usuario'])
    return None


def usuario_tiene_informacion_asociada(usuario):
    cliente = getattr(usuario, 'cliente_taller', None)
    if cliente and (cliente.vehiculos.exists() or cliente.ordenes.exists()):
        return True

    mecanico = getattr(usuario, 'mecanico_taller', None)
    if mecanico and mecanico.ordenes.exists():
        return True

    return False


def redireccion_por_rol(user):
    if user.rol == 'admin':
        return 'admin_dashboard'
    if user.rol == 'cliente':
        return 'cliente_dashboard'
    if user.rol == 'mecanico':
        return 'mecanico_dashboard'
    return None


def rol_requerido(rol):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.rol != rol:
                ruta = redireccion_por_rol(request.user)
                if ruta:
                    return redirect(ruta)
                logout(request)
                return redirect('login')
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def login_view(request):
    if request.user.is_authenticated:
        ruta = redireccion_por_rol(request.user)
        if ruta:
            return redirect(ruta)
        logout(request)

    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''
        now = timezone.now().timestamp()
        failed_attempts = [
            attempt for attempt in request.session.get('login_failed_attempts', [])
            if now - float(attempt) < LOGIN_LOCK_SECONDS
        ]

        if len(failed_attempts) >= LOGIN_MAX_ATTEMPTS:
            request.session['login_failed_attempts'] = failed_attempts
            messages.error(request, 'Demasiados intentos fallidos. Intenta nuevamente en unos minutos.')
            return render(request, 'login.html', {'username_value': username})

        if not username:
            messages.error(request, 'Por favor ingresa tu usuario')
            return render(request, 'login.html')
        if not password:
            messages.error(request, 'Por favor ingresa tu contraseña')
            return render(request, 'login.html', {'username_value': username})
        if any(char.isspace() for char in username) or not USERNAME_RE.fullmatch(username):
            messages.error(request, 'El usuario contiene caracteres no permitidos.')
            return render(request, 'login.html', {'username_value': username})

        user = authenticate(request, username=username, password=password)

        if user is not None:
            ruta = redireccion_por_rol(user)
            if not ruta:
                messages.error(request, 'Tu cuenta no tiene un tipo de acceso válido.')
                return render(request, 'login.html', {'username_value': username})
            login(request, user)
            request.session['last_activity'] = timezone.now().timestamp()
            request.session.pop('login_failed_attempts', None)
            registrar_auditoria(request, 'inicio_sesion', 'Login', f'Inicio de sesion exitoso para {user.username}.')
            return redirect(ruta)

        failed_attempts.append(now)
        request.session['login_failed_attempts'] = failed_attempts
        if len(failed_attempts) >= LOGIN_MAX_ATTEMPTS:
            messages.error(request, 'Demasiados intentos fallidos. Intenta nuevamente en unos minutos.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
        return render(request, 'login.html', {'username_value': username})

    if request.GET.get('next'):
        messages.warning(request, 'Debes iniciar sesión para continuar')
    return render(request, 'login.html')


def logout_view(request):
    if request.user.is_authenticated:
        registrar_auditoria(request, 'cierre_sesion', 'Login', f'Cierre de sesion para {request.user.username}.')
    logout(request)
    return redirect('login')


@rol_requerido('admin')
def admin_dashboard(request):
    from clientes.models import Cliente
    from django.db.models import Sum
    from gastos.models import Gasto
    from herramientas.models import Herramienta
    from mecanicos.models import Mecanico
    from ordenes.models import Orden
    from vehiculos.models import Vehiculo

    inicio_mes = timezone.localdate().replace(day=1)

    ingresos_mes = Orden.objects.filter(
        fecha_ingreso__gte=inicio_mes,
        estado__in=['en_proceso', 'finalizado'],
    ).aggregate(total=Sum('costo_total'))['total'] or 0

    gastos_mes = Gasto.objects.filter(fecha__gte=inicio_mes).aggregate(total=Sum('valor'))['total'] or 0
    costo_repuestos_mes = Orden.objects.filter(
        fecha_ingreso__gte=inicio_mes,
        estado__in=['en_proceso', 'finalizado'],
    ).aggregate(total=Sum('costo_repuestos'))['total'] or 0
    utilidad_estimada = ingresos_mes - gastos_mes - costo_repuestos_mes

    contexto = {
        'total_clientes': Cliente.objects.count(),
        'total_mecanicos_activos': Mecanico.objects.filter(estado='activo').count(),
        'total_vehiculos': Vehiculo.objects.count(),
        'total_ordenes_abiertas': Orden.objects.filter(estado__in=['pendiente', 'en_proceso']).count(),
        'ordenes_pendientes': Orden.objects.filter(estado='pendiente').count(),
        'ordenes_en_proceso': Orden.objects.filter(estado='en_proceso').count(),
        'ordenes_finalizadas': Orden.objects.filter(estado='finalizado').count(),
        'ingresos_mes_formateado': formato_pesos_colombianos(ingresos_mes),
        'gastos_mes_formateado': formato_pesos_colombianos(gastos_mes),
        'costo_repuestos_mes_formateado': formato_pesos_colombianos(costo_repuestos_mes),
        'utilidad_estimada_formateada': formato_pesos_colombianos(utilidad_estimada),
        'herramientas_disponibles': Herramienta.objects.filter(estado='disponible').count(),
        'herramientas_en_uso': Herramienta.objects.filter(estado='en_uso').count(),
        'herramientas_mantenimiento': Herramienta.objects.filter(estado='mantenimiento').count(),
        'mecanicos_ocupados': Mecanico.objects.filter(ordenes__estado='en_proceso').distinct().count(),
        'clientes_prioridad': Cliente.objects.filter(ordenes__prioridad__in=['alta', 'urgente']).distinct().count(),
    }
    return render(request, 'admin_dashboard.html', contexto)


@rol_requerido('cliente')
def cliente_dashboard(request):
    cliente = getattr(request.user, 'cliente_taller', None)
    vehiculos = []
    ordenes = []
    if cliente:
        vehiculos = cliente.vehiculos.all()
        ordenes = cliente.ordenes.select_related('vehiculo', 'mecanico').prefetch_related('evidencias')
    return render(
        request,
        'cliente_dashboard.html',
        {'cliente': cliente, 'vehiculos': vehiculos, 'ordenes': ordenes},
    )


def mecanico_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.rol != 'mecanico':
        if request.user.rol == 'admin':
            return redirect('admin_dashboard')
        if request.user.rol == 'cliente':
            return redirect('cliente_dashboard')
        return redirect('login')

    mecanico = getattr(request.user, 'mecanico_taller', None)
    ordenes = []
    if mecanico:
        ordenes = mecanico.ordenes.select_related('cliente', 'vehiculo')
    return render(
        request,
        'mecanico_dashboard.html',
        {'mecanico': mecanico, 'ordenes': ordenes},
    )


@rol_requerido('admin')
def usuario_lista(request):
    usuarios = Usuario.objects.order_by('username')
    return render(request, 'usuarios/lista.html', {'usuarios': usuarios})


@rol_requerido('admin')
def usuario_crear(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            perfil = asegurar_perfil_por_rol(usuario)
            registrar_auditoria(
                request,
                'creacion_usuario',
                'Personal y accesos',
                f'Se creo la cuenta {usuario.username} con tipo de cuenta {usuario.rol}.',
            )
            messages.success(request, 'Cuenta creada correctamente.')
            if perfil == 'cliente':
                messages.info(request, 'El perfil del cliente fue creado automaticamente.')
            elif perfil == 'mecanico':
                messages.info(request, 'El perfil del mecanico fue creado automaticamente.')
            return redirect('usuarios:lista')
    else:
        form = UsuarioForm()

    return render(request, 'usuarios/crear.html', {'form': form})


@rol_requerido('admin')
def usuario_editar(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        rol_anterior = usuario.rol
        activo_anterior = usuario.is_active
        form = UsuarioEditarForm(request.POST, instance=usuario)
        if form.is_valid():
            usuario = form.save()
            asegurar_perfil_por_rol(usuario)
            registrar_auditoria(
                request,
                'edicion_usuario',
                'Personal y accesos',
                (
                    f'Se actualizo la cuenta {usuario.username}. '
                    f'Rol anterior: {rol_anterior}; rol actual: {usuario.rol}. '
                    f'Activo anterior: {activo_anterior}; activo actual: {usuario.is_active}.'
                ),
            )
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('usuarios:lista')
    else:
        form = UsuarioEditarForm(instance=usuario)

    return render(request, 'usuarios/editar.html', {'form': form, 'usuario_obj': usuario})


@rol_requerido('admin')
def usuario_eliminar(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        if usuario == request.user:
            messages.error(request, 'No puedes eliminar tu propio usuario mientras estas en sesion.')
            return redirect('usuarios:lista')
        if usuario_tiene_informacion_asociada(usuario):
            messages.error(request, 'No se puede eliminar porque tiene información asociada.')
            return redirect('usuarios:lista')
        usuario_eliminado = f'{usuario.username} ({usuario.rol})'
        usuario.delete()
        registrar_auditoria(
            request,
            'eliminacion_usuario',
            'Personal y accesos',
            f'Se elimino la cuenta {usuario_eliminado}.',
        )
        messages.success(request, 'Cuenta eliminada correctamente.')
        if usuario.rol in ['cliente', 'mecanico']:
            messages.info(request, 'Perfil relacionado eliminado correctamente.')
        return redirect('usuarios:lista')

    return render(request, 'usuarios/eliminar.html', {'usuario_obj': usuario})
