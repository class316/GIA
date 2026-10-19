from django import forms

from .models import Repuesto


class RepuestoForm(forms.ModelForm):
    class Meta:
        model = Repuesto
        fields = ['nombre', 'referencia', 'marca', 'cantidad_disponible', 'precio_compra', 'precio_venta', 'proveedor']
        labels = {
            'cantidad_disponible': 'Cantidad disponible',
            'precio_compra': 'Precio de compra',
            'precio_venta': 'Precio de venta',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'referencia': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad_disponible': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'proveedor': forms.TextInput(attrs={'class': 'form-control'}),
        }
        error_messages = {
            'referencia': {'unique': 'Ya existe un repuesto con esta referencia.'},
        }

    def clean_cantidad_disponible(self):
        cantidad = self.cleaned_data.get('cantidad_disponible')
        if cantidad is not None and cantidad < 0:
            raise forms.ValidationError('La cantidad no puede ser negativa.')
        return cantidad

    def clean_precio_compra(self):
        precio = self.cleaned_data.get('precio_compra')
        if precio is not None and precio < 0:
            raise forms.ValidationError('El valor no puede ser negativo.')
        return precio

    def clean_precio_venta(self):
        precio = self.cleaned_data.get('precio_venta')
        if precio is not None and precio < 0:
            raise forms.ValidationError('El valor no puede ser negativo.')
        return precio
