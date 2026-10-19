from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    REQUIRED_FIELDS = ['email', 'rol']

    ROLES = (
        ('admin', 'Administrador'),
        ('cliente', 'Cliente'),
        ('mecanico', 'Mecanico'),
    )

    rol = models.CharField(max_length=10, choices=ROLES, default='cliente')

    def save(self, *args, **kwargs):
        self.is_staff = self.is_superuser or self.rol == 'admin'
        super().save(*args, **kwargs)
