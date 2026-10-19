from django.db import models

from clientes.models import Cliente


class Vehiculo(models.Model):
    placa = models.CharField(max_length=12, unique=True)
    marca = models.CharField(max_length=80)
    modelo = models.CharField(max_length=80)
    anio = models.PositiveIntegerField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='vehiculos')

    class Meta:
        ordering = ['placa']

    def save(self, *args, **kwargs):
        self.placa = self.placa.upper().strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.placa} - {self.marca} {self.modelo} - {self.cliente.nombre}'
