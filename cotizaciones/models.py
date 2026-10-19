from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from clientes.models import Cliente
from mecanicos.models import Mecanico
from repuestos.models import Repuesto
from vehiculos.models import Vehiculo


class Cotizacion(models.Model):
    PRIORIDADES = (
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    )
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('revisada', 'Revisada'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    )

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='cotizaciones')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='cotizaciones')
    descripcion_falla = models.TextField()
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='media')
    mecanico_revisor = models.ForeignKey(
        Mecanico,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='cotizaciones_revisadas',
    )
    diagnostico_mecanico = models.TextField(blank=True)
    servicios_catalogo = models.JSONField(default=list, blank=True)
    repuestos_catalogo = models.ManyToManyField(Repuesto, blank=True, related_name='cotizaciones_recomendadas')
    servicios_sugeridos = models.TextField(blank=True)
    repuestos_recomendados = models.TextField(blank=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')
    costo_estimado = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    observaciones_admin = models.TextField(blank=True)
    fecha = models.DateField(default=timezone.localdate)
    orden_generada = models.OneToOneField(
        'ordenes.Orden',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cotizacion_origen',
    )

    class Meta:
        ordering = ['estado', '-fecha', '-id']

    def __str__(self):
        return f'Cotizacion #{self.pk} - {self.vehiculo.placa}'

# Create your models here.
