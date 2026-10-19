# Generated manually to align GIA admin role with Django staff access.

from django.db import migrations


def sync_admin_staff(apps, schema_editor):
    Usuario = apps.get_model('usuarios', 'Usuario')
    Usuario.objects.filter(rol='admin').update(is_staff=True)


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_alter_usuario_rol'),
    ]

    operations = [
        migrations.RunPython(sync_admin_staff, migrations.RunPython.noop),
    ]
