
from decimal import Decimal

from django.test import TestCase

from clientes.models import Cliente
from repuestos.models import Repuesto
from vehiculos.models import Vehiculo
from ordenes.models import Orden, OrdenRepuesto
from ordenes.forms import OrdenForm, OrdenRepuestoForm


class OrdenModeloTests(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            nombre="Cliente de prueba"
        )

        self.vehiculo = Vehiculo.objects.create(
            placa="TST123",
            marca="Marca de prueba",
            modelo="Modelo de prueba",
            anio=2020,
            cliente=self.cliente,
        )

        self.orden = Orden.objects.create(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            tipo_servicio="revision_general",
            costo_mano_obra=Decimal("50000.00"),
        )

    def test_orden_inicia_con_costos_de_repuestos_en_cero(self):
        self.assertEqual(
            self.orden.costo_repuestos,
            Decimal("0"),
        )
        self.assertEqual(
            self.orden.costo_total,
            Decimal("0"),
        )

    def test_recalcular_costos_actualiza_total(self):
        repuesto = Repuesto.objects.create(
            nombre="Filtro de prueba",
            referencia="TEST-ORDEN-001",
            cantidad_disponible=5,
            precio_compra=Decimal("10000.00"),
            precio_venta=Decimal("15000.00"),
        )

        OrdenRepuesto.objects.create(
            orden=self.orden,
            repuesto=repuesto,
            cantidad=2,
        )

        self.orden.refresh_from_db()

        self.assertEqual(
            self.orden.costo_repuestos,
            Decimal("30000.00"),
        )
        self.assertEqual(
            self.orden.costo_total,
            Decimal("80000.00"),
        )
        self.assertEqual(
            self.orden.costo,
            Decimal("80000.00"),
        )


class OrdenFormTests(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            nombre="Cliente principal"
        )
        self.otro_cliente = Cliente.objects.create(
            nombre="Otro cliente"
        )

        self.vehiculo = Vehiculo.objects.create(
            placa="TST201",
            marca="Marca de prueba",
            modelo="Modelo A",
            anio=2021,
            cliente=self.cliente,
        )

        self.vehiculo_otro_cliente = Vehiculo.objects.create(
            placa="TST202",
            marca="Marca de prueba",
            modelo="Modelo B",
            anio=2022,
            cliente=self.otro_cliente,
        )

    def datos_validos(self):
        return {
            "cliente": self.cliente.pk,
            "vehiculo": self.vehiculo.pk,
            "mecanico": "",
            "tipo_servicio": "revision_general",
            "descripcion": "",
            "falla_reportada": "",
            "diagnostico": "",
            "trabajo_a_realizar": "",
            "prioridad": "media",
            "estado": "pendiente",
            "costo_mano_obra": "50000.00",
            "fecha_ingreso": "2026-10-01",
            "fecha_salida": "",
            "observaciones_mecanico": "",
        }

    def test_formulario_acepta_vehiculo_del_cliente(self):
        form = OrdenForm(data=self.datos_validos())

        self.assertTrue(form.is_valid(), form.errors)

    def test_formulario_rechaza_vehiculo_de_otro_cliente(self):
        datos = self.datos_validos()
        datos["vehiculo"] = self.vehiculo_otro_cliente.pk

        form = OrdenForm(data=datos)

        self.assertFalse(form.is_valid())
        self.assertIn("vehiculo", form.errors)

    def test_formulario_rechaza_fecha_salida_anterior(self):
        datos = self.datos_validos()
        datos["fecha_salida"] = "2026-09-30"

        form = OrdenForm(data=datos)

        self.assertFalse(form.is_valid())
        self.assertIn("fecha_salida", form.errors)


class OrdenRepuestoFormTests(TestCase):
    def setUp(self):
        self.repuesto = Repuesto.objects.create(
            nombre="Filtro de inventario de prueba",
            referencia="TEST-STOCK-001",
            cantidad_disponible=5,
            precio_compra=Decimal("10000.00"),
            precio_venta=Decimal("15000.00"),
        )

    def datos_formulario(self, cantidad):
        return {
            "repuesto": self.repuesto.pk,
            "cantidad": cantidad,
        }

    def test_acepta_cantidad_valida(self):
        form = OrdenRepuestoForm(
            data=self.datos_formulario(2)
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["cantidad"], 2)

    def test_rechaza_cantidad_cero(self):
        form = OrdenRepuestoForm(
            data=self.datos_formulario(0)
        )

        self.assertFalse(form.is_valid())
        self.assertIn("cantidad", form.errors)

    def test_rechaza_cantidad_negativa(self):
        form = OrdenRepuestoForm(
            data=self.datos_formulario(-1)
        )

        self.assertFalse(form.is_valid())
        self.assertIn("cantidad", form.errors)

    def test_rechaza_cantidad_superior_al_stock(self):
        form = OrdenRepuestoForm(
            data=self.datos_formulario(6)
        )

        self.assertFalse(form.is_valid())
        self.assertIn("cantidad", form.errors)

    def test_validar_formulario_no_modifica_inventario(self):
        form = OrdenRepuestoForm(
            data=self.datos_formulario(2)
        )

        self.assertTrue(form.is_valid(), form.errors)

        self.repuesto.refresh_from_db()
        self.assertEqual(self.repuesto.cantidad_disponible, 5)
