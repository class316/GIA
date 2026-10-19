
from decimal import Decimal

from django.test import TestCase

from repuestos.models import Repuesto


class RepuestoModeloTests(TestCase):
    def crear_repuesto(self, cantidad):
        return Repuesto.objects.create(
            nombre="Filtro de aceite de prueba",
            referencia=f"TEST-{cantidad}",
            marca="Marca de prueba",
            cantidad_disponible=cantidad,
            precio_compra=Decimal("10000.00"),
            precio_venta=Decimal("15000.00"),
        )

    def test_cantidad_cero_deja_repuesto_agotado(self):
        repuesto = self.crear_repuesto(0)

        self.assertEqual(repuesto.estado, "agotado")

    def test_cantidad_de_tres_deja_repuesto_en_bajo_stock(self):
        repuesto = self.crear_repuesto(3)

        self.assertEqual(repuesto.estado, "bajo_stock")

    def test_cantidad_de_cuatro_deja_repuesto_disponible(self):
        repuesto = self.crear_repuesto(4)

        self.assertEqual(repuesto.estado, "disponible")

    def test_guardar_actualiza_estado_si_cambia_cantidad(self):
        repuesto = self.crear_repuesto(10)

        repuesto.cantidad_disponible = 0
        repuesto.save()

        repuesto.refresh_from_db()
        self.assertEqual(repuesto.estado, "agotado")
