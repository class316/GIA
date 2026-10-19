from django.core.validators import MinValueValidator
from django.db import models


class Repuesto(models.Model):
    ESTADOS = (
        ('disponible', 'Disponible'),
        ('bajo_stock', 'Bajo stock'),
        ('agotado', 'Agotado'),
    )

    nombre = models.CharField(max_length=120)
    referencia = models.CharField(max_length=80, unique=True)
    marca = models.CharField(max_length=80, blank=True)
    cantidad_disponible = models.PositiveIntegerField(default=0)
    precio_compra = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    precio_venta = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    proveedor = models.CharField(max_length=120, blank=True)
    estado = models.CharField(max_length=14, choices=ESTADOS, default='disponible')

    class Meta:
        ordering = ['nombre']

    def actualizar_estado(self):
        if self.cantidad_disponible <= 0:
            self.estado = 'agotado'
        elif self.cantidad_disponible <= 3:
            self.estado = 'bajo_stock'
        else:
            self.estado = 'disponible'

    def save(self, *args, **kwargs):
        self.actualizar_estado()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.nombre} - {self.referencia}'

# Create your models here.
