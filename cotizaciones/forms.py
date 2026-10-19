from django import forms

from ordenes.models import Orden
from repuestos.models import Repuesto

from .models import Cotizacion


class CotizacionClienteForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = ['vehiculo', 'descripcion_falla', 'prioridad']
        labels = {
            'vehiculo': 'Vehiculo',
            'descripcion_falla': 'Descripcion de la falla',
            'prioridad': 'Prioridad',
        }
        widgets = {
            'vehiculo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion_falla': forms.Textarea(attrs={
                'class': 'form-control gia-textarea',
                'rows': 5,
                'placeholder': 'Describe que le pasa al vehiculo...',
            }),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, cliente=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cliente = cliente
        self.fields['vehiculo'].queryset = cliente.vehiculos.all() if cliente else self.fields['vehiculo'].queryset.none()

    def clean_vehiculo(self):
        vehiculo = self.cleaned_data.get('vehiculo')
        if not vehiculo:
            raise forms.ValidationError('Debes seleccionar un vehiculo.')
        if self.cliente and vehiculo.cliente_id != self.cliente.id:
            raise forms.ValidationError('No puedes cotizar vehiculos de otro cliente.')
        return vehiculo


class CotizacionAdminForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = [
            'mecanico_revisor',
            'diagnostico_mecanico',
            'servicios_sugeridos',
            'repuestos_recomendados',
            'estado',
            'costo_estimado',
            'observaciones_admin',
        ]
        labels = {
            'mecanico_revisor': 'Mecanico revisor',
            'diagnostico_mecanico': 'Diagnostico del mecanico',
            'servicios_sugeridos': 'Servicios sugeridos',
            'repuestos_recomendados': 'Repuestos recomendados',
            'estado': 'Estado',
            'costo_estimado': 'Costo estimado',
            'observaciones_admin': 'Observaciones del administrador',
        }
        widgets = {
            'mecanico_revisor': forms.Select(attrs={'class': 'form-select'}),
            'diagnostico_mecanico': forms.Textarea(attrs={
                'class': 'form-control gia-textarea',
                'rows': 4,
                'placeholder': 'Diagnostico tecnico sugerido por mecanico',
            }),
            'servicios_sugeridos': forms.Textarea(attrs={
                'class': 'form-control gia-textarea',
                'rows': 4,
                'placeholder': 'Servicios sugeridos para el vehiculo',
            }),
            'repuestos_recomendados': forms.Textarea(attrs={
                'class': 'form-control gia-textarea',
                'rows': 4,
                'placeholder': 'Repuestos que el cliente deberia comprar o aprobar',
            }),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'costo_estimado': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'observaciones_admin': forms.Textarea(attrs={
                'class': 'form-control gia-textarea',
                'rows': 4,
                'placeholder': 'Observaciones visibles para el cliente',
            }),
        }

    def clean_costo_estimado(self):
        costo = self.cleaned_data.get('costo_estimado')
        if costo is not None and costo < 0:
            raise forms.ValidationError('El valor no puede ser negativo.')
        return costo


class CotizacionMecanicoForm(forms.ModelForm):
    servicios_existentes = forms.MultipleChoiceField(
        label='Servicios existentes',
        choices=Orden.TIPOS_SERVICIO,
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '8'}),
        help_text='Puedes seleccionar uno o varios servicios del catalogo.',
    )

    class Meta:
        model = Cotizacion
        fields = [
            'diagnostico_mecanico',
            'servicios_existentes',
            'repuestos_catalogo',
            'servicios_sugeridos',
            'repuestos_recomendados',
        ]
        labels = {
            'diagnostico_mecanico': 'Diagnostico tecnico',
            'repuestos_catalogo': 'Repuestos del inventario',
            'servicios_sugeridos': 'Comentario sobre servicios recomendados',
            'repuestos_recomendados': 'Comentario sobre repuestos recomendados',
        }
        widgets = {
            'diagnostico_mecanico': forms.Textarea(attrs={
                'class': 'form-control gia-textarea',
                'rows': 4,
                'placeholder': 'Indica que puede estar fallando y que se debe revisar',
            }),
            'repuestos_catalogo': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '8'}),
            'servicios_sugeridos': forms.Textarea(attrs={
                'class': 'form-control gia-textarea',
                'rows': 4,
                'placeholder': 'Explica por que recomiendas esos servicios (opcional)',
            }),
            'repuestos_recomendados': forms.Textarea(attrs={
                'class': 'form-control gia-textarea',
                'rows': 4,
                'placeholder': 'Notas sobre repuestos, cantidades o referencias que no esten en inventario (opcional)',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['repuestos_catalogo'].queryset = Repuesto.objects.order_by('nombre')
        if self.instance and self.instance.pk:
            self.fields['servicios_existentes'].initial = self.instance.servicios_catalogo

    def save(self, commit=True):
        cotizacion = super().save(commit=False)
        cotizacion.servicios_catalogo = self.cleaned_data.get('servicios_existentes') or []
        if commit:
            cotizacion.save()
            self.save_m2m()
        return cotizacion
