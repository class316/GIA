from django.conf import settings
from django.db import models


class Cliente(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'cliente'},
        related_name='cliente_taller',
    )
    nombre = models.CharField(max_length=120)
    telefono = models.CharField(max_length=15, blank=True)
    correo = models.EmailField(unique=True, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        contacto = self.telefono or self.correo or 'Correo no registrado'
        return f'{self.nombre} - {contacto}'
