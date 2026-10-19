from django import forms

from .models import Gasto


class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ['concepto', 'categoria', 'valor', 'fecha', 'descripcion']
        widgets = {
            'concepto': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control gia-textarea',
                'rows': 4,
                'placeholder': 'Informacion adicional (opcional)',
            }),
        }

    def clean_valor(self):
        valor = self.cleaned_data.get('valor')
        if valor is not None and valor < 0:
            raise forms.ValidationError('El valor no puede ser negativo.')
        return valor
