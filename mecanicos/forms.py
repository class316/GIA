import re

from django import forms
from django.db.models import Q

from usuarios.models import Usuario

from .models import Mecanico


NOMBRE_RE = re.compile(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$')


class MecanicoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        filtro = Q(rol='mecanico', mecanico_taller__isnull=True)
        if self.instance and self.instance.usuario_id:
            filtro |= Q(pk=self.instance.usuario_id)

        self.fields['usuario'].queryset = Usuario.objects.filter(filtro).order_by('username')
        self.fields['usuario'].empty_label = 'Selecciona una cuenta de mecánico'
        self.fields['usuario'].help_text = (
            'Aquí aparecen las cuentas creadas en Personal y accesos con rol mecánico '
            'que todavía no tienen perfil en Equipo mecánico.'
        )
        self.fields['usuario'].error_messages['invalid_choice'] = (
            'Solo puedes relacionar cuentas con rol mecánico que no tengan perfil mecánico.'
        )

    class Meta:
        model = Mecanico
        fields = ['usuario', 'nombre', 'telefono', 'correo', 'especialidad', 'estado']
        labels = {
            'usuario': 'Cuenta de acceso del mecánico',
            'nombre': 'Nombre completo',
            'telefono': 'Teléfono',
            'correo': 'Correo',
            'especialidad': 'Especialidad',
            'estado': 'Estado',
        }
        widgets = {
            'usuario': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'especialidad': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError('El nombre es obligatorio')
        if not NOMBRE_RE.fullmatch(nombre):
            raise forms.ValidationError('El nombre no puede contener números')
        return nombre

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').strip()
        if not telefono:
            return telefono
        if not telefono.isdigit():
            raise forms.ValidationError('El teléfono solo debe contener números')
        return telefono

    def clean_correo(self):
        correo = (self.cleaned_data.get('correo') or '').strip().lower()
        if not correo:
            return None
        if Mecanico.objects.exclude(pk=self.instance.pk).filter(correo__iexact=correo).exists():
            raise forms.ValidationError('Ya existe un registro con ese correo')
        return correo

    def clean_especialidad(self):
        especialidad = self.cleaned_data.get('especialidad', '').strip()
        if not especialidad:
            raise forms.ValidationError('La especialidad es obligatoria')
        return especialidad

    def clean_usuario(self):
        usuario = self.cleaned_data.get('usuario')
        if not usuario:
            return usuario
        if usuario.rol != 'mecanico':
            raise forms.ValidationError('Solo puedes relacionar cuentas con rol mecánico')
        if Mecanico.objects.exclude(pk=self.instance.pk).filter(usuario=usuario).exists():
            raise forms.ValidationError('Esa cuenta ya está relacionada con otro mecánico')
        return usuario
