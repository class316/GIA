from django import forms

from .models import Herramienta


class HerramientaForm(forms.ModelForm):
    class Meta:
        model = Herramienta
        fields = [
            'nombre',
            'tipo',
            'codigo_interno',
            'estado',
            'ubicacion',
            'mecanico_asignado',
            'fecha_ultimo_mantenimiento',
            'observaciones',
        ]
        labels = {
            'codigo_interno': 'Codigo interno',
            'mecanico_asignado': 'Mecanico asignado',
            'fecha_ultimo_mantenimiento': 'Fecha ultimo mantenimiento',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'codigo_interno': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'mecanico_asignado': forms.Select(attrs={'class': 'form-select'}),
            'fecha_ultimo_mantenimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control gia-textarea',
                'rows': 4,
                'placeholder': 'Puedes escribir alguna observacion (opcional)',
            }),
        }
        error_messages = {
            'codigo_interno': {'unique': 'Ya existe una herramienta o equipo con este codigo.'},
        }

    def clean(self):
        cleaned = super().clean()
        estado = cleaned.get('estado')
        mecanico = cleaned.get('mecanico_asignado')
        if estado == 'fuera_servicio' and mecanico:
            self.add_error('mecanico_asignado', 'No puedes asignar una herramienta fuera de servicio.')
        return cleaned
