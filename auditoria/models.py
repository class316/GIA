import hashlib

from django.conf import settings
from django.db import models
from django.utils import timezone


class Auditoria(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auditorias_seguridad',
    )
    usuario_identificador = models.CharField(max_length=150, blank=True)
    accion = models.CharField(max_length=120)
    modulo = models.CharField(max_length=120)
    descripcion = models.TextField()
    fecha_hora = models.DateTimeField(default=timezone.now)
    ip = models.GenericIPAddressField(null=True, blank=True)
    hash_anterior = models.CharField(max_length=64, blank=True)
    hash_actual = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ['-fecha_hora', '-id']
        verbose_name = 'Auditoria de seguridad'
        verbose_name_plural = 'Auditorias de seguridad'

    def __str__(self):
        return f'{self.fecha_hora:%Y-%m-%d %H:%M} - {self.modulo} - {self.accion}'

    def datos_para_hash(self):
        fecha = self.fecha_hora.isoformat() if self.fecha_hora else ''
        usuario = self.usuario_identificador or ''
        return f'{usuario}|{self.accion}|{self.modulo}|{self.descripcion}|{fecha}|{self.hash_anterior}'

    def calcular_hash(self):
        return hashlib.sha256(self.datos_para_hash().encode('utf-8')).hexdigest()
