from django.conf import settings
from django.db import models


class Mecanico(models.Model):
    ESTADOS = (
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    )

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'mecanico'},
        related_name='mecanico_taller',
    )
    nombre = models.CharField(max_length=120)
    telefono = models.CharField(max_length=15, blank=True)
    correo = models.EmailField(unique=True, blank=True, null=True)
    especialidad = models.CharField(max_length=120, default='Sin asignar')
    estado = models.CharField(max_length=10, choices=ESTADOS, default='activo')

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
