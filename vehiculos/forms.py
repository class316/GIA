from django import forms
from django.utils import timezone

from .models import Vehiculo


class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['placa', 'marca', 'modelo', 'anio', 'cliente']
        labels = {
            'placa': 'Placa',
            'marca': 'Marca',
            'modelo': 'Modelo',
            'anio': 'Año',
            'cliente': 'Cliente dueño del vehículo',
        }
        widgets = {
            'placa': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'anio': forms.NumberInput(attrs={'class': 'form-control'}),
            'cliente': forms.Select(attrs={'class': 'form-select'}),
        }
        error_messages = {
            'cliente': {'required': 'Debes seleccionar un cliente.'},
            'placa': {'required': 'La placa es obligatoria.'},
            'marca': {'required': 'La marca es obligatoria.'},
            'modelo': {'required': 'El modelo es obligatorio.'},
            'anio': {'required': 'El año es obligatorio.', 'invalid': 'El año debe ser numérico.'},
        }

    def clean_placa(self):
        placa = self.cleaned_data.get('placa', '').strip().upper()
        if not placa:
            raise forms.ValidationError('La placa es obligatoria.')
        if Vehiculo.objects.exclude(pk=self.instance.pk).filter(placa__iexact=placa).exists():
            raise forms.ValidationError('La placa ya está registrada.')
        return placa

    def clean_marca(self):
        marca = self.cleaned_data.get('marca', '').strip()
        if not marca:
            raise forms.ValidationError('La marca es obligatoria.')
        return marca

    def clean_modelo(self):
        modelo = self.cleaned_data.get('modelo', '').strip()
        if not modelo:
            raise forms.ValidationError('El modelo es obligatorio.')
        return modelo

    def clean_anio(self):
        anio = self.cleaned_data.get('anio')
        actual = timezone.localdate().year
        if anio is None or anio < 1950 or anio > actual:
            raise forms.ValidationError(f'El año debe estar entre 1950 y {actual}.')
        return anio

    def clean_cliente(self):
        cliente = self.cleaned_data.get('cliente')
        if not cliente:
            raise forms.ValidationError('Debes seleccionar un cliente.')
        return cliente
