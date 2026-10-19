# Generated manually for the GIA role default.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='rol',
            field=models.CharField(
                choices=[
                    ('admin', 'Administrador'),
                    ('cliente', 'Cliente'),
                    ('mecanico', 'Mecanico'),
                ],
                default='cliente',
                max_length=10,
            ),
        ),
    ]
