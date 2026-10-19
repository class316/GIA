from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Gasto(models.Model):
    CATEGORIAS = (
        ('arriendo', 'Arriendo'),
        ('servicios', 'Servicios'),
        ('nomina', 'Nomina'),
        ('repuestos', 'Repuestos'),
        ('mantenimiento', 'Mantenimiento'),
        ('herramientas', 'Herramientas'),
        ('otros', 'Otros'),
    )

    concepto = models.CharField(max_length=140)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    valor = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    fecha = models.DateField(default=timezone.localdate)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha', 'concepto']

    def __str__(self):
        return f'{self.concepto} - {self.valor}'

# Create your models here.
