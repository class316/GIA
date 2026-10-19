from django.core.management.base import BaseCommand

from herramientas.models import Herramienta


HERRAMIENTAS_BASE = [
    ('Elevador hidraulico de vehiculos', 'elevador', 3, 'Zona elevadores'),
    ('Alineador de ruedas', 'alineador', 2, 'Zona alineacion'),
    ('Maquina de equilibrado de neumaticos', 'montallantas', 1, 'Zona llantas'),
    ('Montallantas', 'montallantas', 1, 'Zona llantas'),
    ('Escaner de diagnostico automotriz', 'escaner', 2, 'Diagnostico'),
    ('Computadora de diagnostico', 'escaner', 1, 'Diagnostico'),
    ('Multimetro automotriz', 'especializada', 2, 'Diagnostico'),
    ('Manometro automotriz', 'especializada', 2, 'Diagnostico'),
    ('Medidor de compresion', 'especializada', 1, 'Motores'),
    ('Detector de fugas', 'especializada', 1, 'Diagnostico'),
    ('Analizador de gases de escape', 'especializada', 1, 'Diagnostico'),
    ('Compresor de aire', 'compresor', 2, 'Zona neumatica'),
    ('Llave dinamometrica', 'torquimetro', 2, 'Herramienta especializada'),
    ('Llave de torque', 'torquimetro', 2, 'Herramienta especializada'),
    ('Llave de impacto neumatica', 'especializada', 2, 'Zona neumatica'),
    ('Pistola de impacto electrica', 'especializada', 2, 'Herramienta especializada'),
    ('Gato hidraulico', 'especializada', 3, 'Zona elevadores'),
    ('Prensa hidraulica', 'especializada', 1, 'Banco de trabajo'),
    ('Prensa o tornillo de banco', 'manual', 2, 'Banco de trabajo'),
    ('Polipasto', 'especializada', 1, 'Motores'),
    ('Estacion de limpieza de piezas', 'especializada', 1, 'Lavado de piezas'),
    ('Estacion de trabajo', 'otro', 3, 'Bahias de trabajo'),
    ('Juego de llaves de boca fija y ajustable', 'manual', 3, 'Herramienta manual'),
    ('Juego de llaves allen', 'manual', 3, 'Herramienta manual'),
    ('Juego de llaves de vaso', 'manual', 3, 'Herramienta manual'),
    ('Juego de llaves mixtas', 'manual', 3, 'Herramienta manual'),
    ('Juego de destornilladores', 'manual', 4, 'Herramienta manual'),
    ('Alicates de punta corte y presion', 'manual', 3, 'Herramienta manual'),
    ('Alicates para anillos de seguridad', 'manual', 2, 'Herramienta manual'),
    ('Juego de calibradores', 'especializada', 2, 'Medicion'),
    ('Extractor de rodamientos', 'especializada', 1, 'Herramienta especializada'),
    ('Extractor de cojinetes', 'especializada', 1, 'Herramienta especializada'),
    ('Extractor de volante', 'especializada', 1, 'Herramienta especializada'),
    ('Extractor de engranajes', 'especializada', 1, 'Herramienta especializada'),
    ('Juego de herramientas para frenos', 'especializada', 2, 'Frenos'),
    ('Juego de herramientas de compresion de resortes de valvulas', 'especializada', 1, 'Motores'),
    ('Pistola de engrase', 'especializada', 1, 'Lubricacion'),
    ('Pistola de calor', 'especializada', 1, 'Electricidad'),
    ('Herramienta de eliminacion de abolladuras', 'especializada', 1, 'Latoneria'),
    ('Llave de filtro de aceite', 'manual', 2, 'Lubricacion'),
    ('Dado para bujias', 'manual', 2, 'Motores'),
    ('Cargador de bateria', 'especializada', 1, 'Electricidad'),
]


def codigo_base(nombre):
    limpio = ''.join(caracter for caracter in nombre.upper() if caracter.isalnum())
    return limpio[:12] or 'HERRAMIENTA'


class Command(BaseCommand):
    help = 'Carga un inventario base de herramientas y equipos importantes para el taller.'

    def handle(self, *args, **options):
        creados = 0
        existentes = 0

        for nombre, tipo, cantidad, ubicacion in HERRAMIENTAS_BASE:
            base = codigo_base(nombre)
            for numero in range(1, cantidad + 1):
                codigo = f'{base}-{numero:02d}'
                _, created = Herramienta.objects.get_or_create(
                    codigo_interno=codigo,
                    defaults={
                        'nombre': nombre,
                        'tipo': tipo,
                        'estado': 'disponible',
                        'ubicacion': ubicacion,
                    },
                )
                creados += int(created)
                existentes += int(not created)

        self.stdout.write(self.style.SUCCESS(
            f'Herramientas creadas: {creados}. Ya existian: {existentes}. Total: {Herramienta.objects.count()}.'
        ))
