from django.db import models
from django.utils import timezone
from django.conf import settings

from clientes.models import Cliente
from mecanicos.models import Mecanico
from vehiculos.models import Vehiculo


class Orden(models.Model):
    TIPOS_SERVICIO = (
        ('revision_general', 'Revision general - $60.000 COP'),
        ('diagnostico_escaner', 'Diagnostico con escaner - $99.000 COP'),
        ('cambio_aceite', 'Cambio de aceite y filtro - $280.000 COP'),
        ('mantenimiento_preventivo', 'Mantenimiento preventivo basico - $420.000 COP'),
        ('pastillas_freno', 'Cambio de pastillas de freno - $220.000 COP'),
        ('frenos_completo', 'Servicio completo de frenos - $480.000 COP'),
        ('alineacion_balanceo', 'Alineacion y balanceo - $170.000 COP'),
        ('cambio_bateria', 'Cambio de bateria - $420.000 COP'),
        ('reparacion_suspension_menor', 'Suspension menor - bujes/terminales - $250.000 COP'),
        ('reparacion_suspension', 'Suspension completa promedio - $1.100.000 COP'),
        ('cambio_amortiguadores', 'Cambio de amortiguadores - $850.000 COP'),
        ('sincronizacion_motor', 'Sincronizacion de motor - $320.000 COP'),
        ('correa_reparticion', 'Cambio correa de reparticion - $750.000 COP'),
        ('kit_embrague', 'Cambio kit de embrague - $1.250.000 COP'),
        ('aire_acondicionado', 'Revision aire acondicionado - $220.000 COP'),
        ('cambio_llantas', 'Cambio e instalacion de llantas - $180.000 COP'),
        ('reparacion_electrica', 'Diagnostico/reparacion electrica - $180.000 COP'),
        ('reparacion_motor', 'Reparacion de motor parcial - $1.800.000 COP'),
        ('otro', 'Otro servicio'),
    )

    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En proceso'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    )
    PRIORIDADES = (
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    )

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='ordenes')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='ordenes')
    mecanico = models.ForeignKey(
        Mecanico,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name='ordenes',
    )
    tipo_servicio = models.CharField(max_length=40, choices=TIPOS_SERVICIO, default='revision_general')
    descripcion = models.TextField(blank=True)
    falla_reportada = models.TextField(blank=True)
    diagnostico = models.TextField(blank=True)
    trabajo_a_realizar = models.TextField(blank=True)
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='media')
    estado = models.CharField(max_length=12, choices=ESTADOS, default='pendiente')
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_mano_obra = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    costo_repuestos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    costo_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    observaciones_mecanico = models.TextField(blank=True)
    fecha_ingreso = models.DateField(default=timezone.localdate)
    fecha_salida = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['-fecha_ingreso', '-id']

    def __str__(self):
        return f'Orden #{self.pk} - {self.vehiculo.placa}'

    def recalcular_costos(self, guardar=True):
        total_repuestos = sum(item.subtotal for item in self.repuestos_usados.all()) if self.pk else 0
        self.costo_repuestos = total_repuestos
        self.costo_total = (self.costo_mano_obra or 0) + (self.costo_repuestos or 0)
        self.costo = self.costo_total
        if guardar:
            self.save(update_fields=['costo_repuestos', 'costo_total', 'costo'])


class OrdenRepuesto(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='repuestos_usados')
    repuesto = models.ForeignKey('repuestos.Repuesto', on_delete=models.PROTECT, related_name='usos_en_ordenes')
    cantidad = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ['repuesto__nombre']

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.repuesto.precio_venta
        super().save(*args, **kwargs)
        self.orden.recalcular_costos()

    def __str__(self):
        return f'{self.repuesto} x {self.cantidad}'


class OrdenHerramienta(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='herramientas_necesarias')
    herramienta = models.ForeignKey('herramientas.Herramienta', on_delete=models.PROTECT, related_name='ordenes_asignadas')

    class Meta:
        ordering = ['herramienta__nombre']
        unique_together = ('orden', 'herramienta')

    def __str__(self):
        return f'{self.orden} - {self.herramienta}'


def evidencia_upload_path(instance, filename):
    return f'evidencias/orden_{instance.orden_id}/{filename}'


class EvidenciaOrden(models.Model):
    TIPOS = (
        ('antes', 'Antes'),
        ('durante', 'Durante'),
        ('despues', 'Despues'),
    )

    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='evidencias')
    imagen = models.FileField(upload_to=evidencia_upload_path)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=12, choices=TIPOS)
    fecha_hora = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evidencias_ordenes',
    )

    class Meta:
        ordering = ['-fecha_hora', '-id']

    def __str__(self):
        return f'Evidencia {self.get_tipo_display()} - Orden #{self.orden_id}'
