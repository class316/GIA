from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from clientes.models import Cliente
from ordenes.models import Orden, OrdenRepuesto
from repuestos.models import Repuesto
from vehiculos.models import Vehiculo


class InventarioOrdenTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.admin = User.objects.create_user(
            username="admin_inventario_test",
            password="PruebaSegura123!",
            rol="admin",
        )
        cls.cliente = Cliente.objects.create(nombre="Cliente de prueba")
        cls.vehiculo = Vehiculo.objects.create(
            placa="TST123",
            marca="Marca de prueba",
            modelo="Modelo de prueba",
            anio=2020,
            cliente=cls.cliente,
        )

    def setUp(self):
        self.client.force_login(self.admin)

        self.orden = Orden.objects.create(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            tipo_servicio="revision_general",
            costo_mano_obra=Decimal("50000.00"),
            costo_repuestos=Decimal("0.00"),
            costo_total=Decimal("50000.00"),
            costo=Decimal("50000.00"),
)

        self.repuesto = Repuesto.objects.create(
            nombre="Filtro de prueba",
            referencia="TEST-ORDEN-001",
            cantidad_disponible=5,
            precio_compra=Decimal("10000.00"),
            precio_venta=Decimal("15000.00"),
        )

    def enviar_repuesto(self, cantidad):
        return self.client.post(
            reverse("ordenes:agregar_repuesto", args=[self.orden.pk]),
            {"repuesto": self.repuesto.pk, "cantidad": cantidad},
        )

    def test_agregar_repuesto_descuenta_stock_y_actualiza_costos(self):
        respuesta = self.enviar_repuesto(2)
        self.assertEqual(respuesta.status_code, 302)
        self.repuesto.refresh_from_db()
        self.orden.refresh_from_db()
        self.assertEqual(self.repuesto.cantidad_disponible, 3)
        self.assertEqual(self.repuesto.estado, "bajo_stock")
        self.assertEqual(OrdenRepuesto.objects.filter(orden=self.orden, repuesto=self.repuesto).count(), 1)
        self.assertEqual(self.orden.costo_repuestos, Decimal("30000.00"))
        self.assertEqual(self.orden.costo_total, Decimal("80000.00"))

    def test_no_descuenta_stock_si_cantidad_supera_existencias(self):
        respuesta = self.enviar_repuesto(6)
        self.assertEqual(respuesta.status_code, 200)
        self.repuesto.refresh_from_db()
        self.orden.refresh_from_db()
        self.assertEqual(self.repuesto.cantidad_disponible, 5)
        self.assertEqual(OrdenRepuesto.objects.filter(orden=self.orden, repuesto=self.repuesto).count(), 0)
        self.assertEqual(self.orden.costo_repuestos, Decimal("0.00"))
        self.assertEqual(self.orden.costo_total, Decimal("50000.00"))

    def test_revierte_stock_si_falla_guardado_del_item(self):
        with patch(
            "ordenes.models.OrdenRepuesto.save",
            side_effect=RuntimeError("Error simulado de guardado"),
        ):
            respuesta = self.enviar_repuesto(2)
        self.assertEqual(respuesta.status_code, 200)
        self.repuesto.refresh_from_db()
        self.orden.refresh_from_db()
        self.assertEqual(self.repuesto.cantidad_disponible, 5)
        self.assertEqual(self.repuesto.estado, "disponible")
        self.assertEqual(OrdenRepuesto.objects.filter(orden=self.orden, repuesto=self.repuesto).count(), 0)
        self.assertEqual(self.orden.costo_repuestos, Decimal("0.00"))
        self.assertEqual(self.orden.costo_total, Decimal("50000.00"))

    def test_agotar_stock_actualiza_estado(self):
        respuesta = self.enviar_repuesto(5)
        self.assertEqual(respuesta.status_code, 302)
        self.repuesto.refresh_from_db()
        self.orden.refresh_from_db()
        self.assertEqual(self.repuesto.cantidad_disponible, 0)
        self.assertEqual(self.repuesto.estado, "agotado")
        self.assertEqual(self.orden.costo_repuestos, Decimal("75000.00"))
        self.assertEqual(self.orden.costo_total, Decimal("125000.00"))

    def test_usuario_sin_permiso_no_modifica_inventario(self):
        self.client.logout()
        respuesta = self.enviar_repuesto(2)
        self.assertEqual(respuesta.status_code, 302)
        self.repuesto.refresh_from_db()
        self.assertEqual(self.repuesto.cantidad_disponible, 5)
        self.assertEqual(OrdenRepuesto.objects.filter(orden=self.orden, repuesto=self.repuesto).count(), 0)
