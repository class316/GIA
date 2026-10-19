from django.db import models

from mecanicos.models import Mecanico


class Herramienta(models.Model):
    TIPOS = (
        ('manual', 'Herramienta manual'),
        ('especializada', 'Herramienta especializada'),
        ('elevador', 'Elevador'),
        ('montallantas', 'Montallantas'),
        ('alineador', 'Alineador'),
        ('escaner', 'Escaner'),
        ('torquimetro', 'Torquimetro'),
        ('compresor', 'Compresor'),
        ('otro', 'Otro'),
    )
    ESTADOS = (
        ('disponible', 'Disponible'),
        ('en_uso', 'En uso'),
        ('mantenimiento', 'Mantenimiento'),
        ('fuera_servicio', 'Fuera de servicio'),
    )

    nombre = models.CharField(max_length=120)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    codigo_interno = models.CharField(max_length=60, unique=True)
    estado = models.CharField(max_length=18, choices=ESTADOS, default='disponible')
    ubicacion = models.CharField(max_length=120, blank=True)
    mecanico_asignado = models.ForeignKey(
        Mecanico,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='herramientas_asignadas',
    )
    fecha_ultimo_mantenimiento = models.DateField(blank=True, null=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['nombre']

    @property
    def esta_disponible(self):
        return self.estado == 'disponible'

    def __str__(self):
        return f'{self.nombre} ({self.codigo_interno})'

# Create your models here.
