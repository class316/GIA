from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from clientes.models import Cliente
from mecanicos.models import Mecanico
from vehiculos.models import Vehiculo
from ordenes.models import Orden


Usuario = get_user_model()


class PermisosOrdenesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = Usuario.objects.create_user(
            username="admin_prueba",
            password="ClavePrueba-123!",
            rol="admin",
        )
        cls.usuario_cliente = Usuario.objects.create_user(
            username="cliente_prueba",
            password="ClavePrueba-123!",
            rol="cliente",
        )
        cls.usuario_mecanico = Usuario.objects.create_user(
            username="mecanico_prueba",
            password="ClavePrueba-123!",
            rol="mecanico",
        )
        cls.otro_usuario_mecanico = Usuario.objects.create_user(
            username="mecanico_otro",
            password="ClavePrueba-123!",
            rol="mecanico",
        )

        cls.cliente = Cliente.objects.create(
            usuario=cls.usuario_cliente,
            nombre="Cliente de prueba",
        )
        cls.otro_cliente = Cliente.objects.create(
            nombre="Otro cliente de prueba",
        )
        cls.mecanico = Mecanico.objects.create(
            usuario=cls.usuario_mecanico,
            nombre="Mecanico de prueba",
        )
        cls.otro_mecanico = Mecanico.objects.create(
            usuario=cls.otro_usuario_mecanico,
            nombre="Otro mecanico de prueba",
        )

        cls.vehiculo = Vehiculo.objects.create(
            placa="TST001",
            marca="Marca de prueba",
            modelo="Modelo de prueba",
            anio=2020,
            cliente=cls.cliente,
        )
        cls.vehiculo_otro_cliente = Vehiculo.objects.create(
            placa="TST002",
            marca="Marca de prueba",
            modelo="Modelo de prueba",
            anio=2021,
            cliente=cls.otro_cliente,
        )

        cls.orden_propia = Orden.objects.create(
            cliente=cls.cliente,
            vehiculo=cls.vehiculo,
            mecanico=cls.mecanico,
            tipo_servicio="revision_general",
            fecha_ingreso=date(2026, 1, 10),
            estado="en_proceso",
            costo_mano_obra=Decimal("10000.00"),
        )
        cls.orden_ajena = Orden.objects.create(
            cliente=cls.otro_cliente,
            vehiculo=cls.vehiculo_otro_cliente,
            mecanico=cls.otro_mecanico,
            tipo_servicio="revision_general",
            fecha_ingreso=date(2026, 1, 11),
            estado="en_proceso",
            costo_mano_obra=Decimal("20000.00"),
        )

    def test_usuario_anonimo_no_accede_a_lista_de_ordenes(self):
        respuesta = self.client.get(reverse("ordenes:lista"))

        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse("login"), respuesta.url)

    def test_cliente_no_accede_a_lista_exclusiva_del_admin(self):
        self.client.force_login(self.usuario_cliente)

        respuesta = self.client.get(reverse("ordenes:lista"))

        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse("cliente_dashboard"), respuesta.url)

    def test_cliente_no_consulta_evidencias_de_orden_ajena(self):
        self.client.force_login(self.usuario_cliente)

        respuesta = self.client.get(
            reverse("ordenes:evidencias", args=[self.orden_ajena.pk])
        )

        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta.url, reverse("cliente_dashboard"))

    def test_mecanico_no_actualiza_orden_asignada_a_otro(self):
        self.client.force_login(self.usuario_mecanico)
        estado_original = self.orden_ajena.estado

        respuesta = self.client.post(
            reverse("mecanico_actualizar", args=[self.orden_ajena.pk]),
            {
                "estado": "finalizado",
                "diagnostico": "Prueba de permisos",
                "trabajo_a_realizar": "Prueba de permisos",
                "costo_mano_obra": "999999",
                "observaciones_mecanico": "Prueba automatizada",
            },
        )

        self.orden_ajena.refresh_from_db()

        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(self.orden_ajena.estado, estado_original)
        self.assertEqual(
            self.orden_ajena.costo_mano_obra,
            Decimal("20000.00"),
        )

    def test_cliente_puede_ver_su_galeria_de_evidencias(self):
        self.client.force_login(self.usuario_cliente)

        respuesta = self.client.get(
            reverse("ordenes:evidencias", args=[self.orden_propia.pk])
        )

        self.assertEqual(respuesta.status_code, 200)
