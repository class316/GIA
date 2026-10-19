from django.core.management.base import BaseCommand

from repuestos.models import Repuesto


REPUESTOS_BASE = [
    ('Aceite motor 10W40 galon', 'ACE-10W40', 'Mobil', 12, 95000, 135000, 'Proveedor lubricantes'),
    ('Aceite motor 5W30 sintetico galon', 'ACE-5W30', 'Castrol', 10, 125000, 175000, 'Proveedor lubricantes'),
    ('Filtro de aceite universal', 'FIL-ACE-001', 'Mann', 20, 18000, 35000, 'Proveedor filtros'),
    ('Filtro de aire motor', 'FIL-AIR-001', 'Mann', 15, 30000, 55000, 'Proveedor filtros'),
    ('Filtro de cabina', 'FIL-CAB-001', 'Mann', 12, 28000, 50000, 'Proveedor filtros'),
    ('Bujias juego x4', 'BUJ-JGO-004', 'NGK', 10, 65000, 120000, 'Proveedor encendido'),
    ('Pastillas de freno delanteras', 'FRE-PAST-DEL', 'Bosch', 8, 90000, 165000, 'Proveedor frenos'),
    ('Pastillas de freno traseras', 'FRE-PAST-TRA', 'Bosch', 8, 85000, 155000, 'Proveedor frenos'),
    ('Discos de freno delanteros par', 'FRE-DISC-DEL', 'Fremax', 5, 180000, 320000, 'Proveedor frenos'),
    ('Liquido de frenos DOT4', 'FRE-DOT4', 'Varga', 16, 18000, 38000, 'Proveedor frenos'),
    ('Bateria 12V 60Ah', 'BAT-60AH', 'Mac', 5, 280000, 430000, 'Proveedor baterias'),
    ('Bornes de bateria par', 'BAT-BORNES', 'Generico', 12, 9000, 25000, 'Proveedor baterias'),
    ('Amortiguador delantero unidad', 'SUS-AMO-DEL', 'Monroe', 6, 170000, 290000, 'Proveedor suspension'),
    ('Amortiguador trasero unidad', 'SUS-AMO-TRA', 'Monroe', 6, 145000, 250000, 'Proveedor suspension'),
    ('Buje de tijera', 'SUS-BUJE-TIJ', 'Generico', 12, 25000, 65000, 'Proveedor suspension'),
    ('Rotula suspension', 'SUS-ROTULA', 'TRW', 10, 55000, 110000, 'Proveedor suspension'),
    ('Terminal de direccion', 'SUS-TERM-DIR', 'TRW', 10, 45000, 95000, 'Proveedor suspension'),
    ('Bieleta estabilizadora', 'SUS-BIELETA', 'TRW', 10, 35000, 85000, 'Proveedor suspension'),
    ('Correa de reparticion', 'MOT-COR-REP', 'Gates', 5, 130000, 240000, 'Proveedor motor'),
    ('Tensor correa reparticion', 'MOT-TENSOR', 'Gates', 5, 120000, 230000, 'Proveedor motor'),
    ('Bomba de agua', 'MOT-BOM-AGUA', 'GMB', 4, 145000, 280000, 'Proveedor motor'),
    ('Kit embrague', 'EMB-KIT-001', 'Valeo', 3, 520000, 950000, 'Proveedor embrague'),
    ('Gas refrigerante aire acondicionado', 'AIRE-GAS-R134', 'Generico', 6, 55000, 120000, 'Proveedor aire'),
    ('Valvula rin', 'LLA-VALVULA', 'Generico', 50, 3000, 10000, 'Proveedor llantas'),
    ('Contrapesas balanceo juego', 'LLA-CONTRA', 'Generico', 30, 8000, 20000, 'Proveedor llantas'),
    ('Fusibles automotrices juego', 'ELE-FUS-JGO', 'Generico', 20, 8000, 22000, 'Proveedor electrico'),
    ('Rele automotriz', 'ELE-RELE', 'Generico', 10, 12000, 30000, 'Proveedor electrico'),
    ('Sensor oxigeno universal', 'ELE-SENS-O2', 'Bosch', 3, 140000, 260000, 'Proveedor electrico'),
]


class Command(BaseCommand):
    help = 'Carga repuestos comunes asociados a servicios automotrices.'

    def handle(self, *args, **options):
        creados = 0
        existentes = 0
        for nombre, referencia, marca, cantidad, compra, venta, proveedor in REPUESTOS_BASE:
            _, created = Repuesto.objects.get_or_create(
                referencia=referencia,
                defaults={
                    'nombre': nombre,
                    'marca': marca,
                    'cantidad_disponible': cantidad,
                    'precio_compra': compra,
                    'precio_venta': venta,
                    'proveedor': proveedor,
                },
            )
            creados += int(created)
            existentes += int(not created)
        self.stdout.write(self.style.SUCCESS(
            f'Repuestos creados: {creados}. Ya existian: {existentes}. Total: {Repuesto.objects.count()}.'
        ))
