
from django import forms
from django.core.exceptions import ValidationError

from mecanicos.models import Mecanico

from .models import EvidenciaOrden, Orden, OrdenHerramienta, OrdenRepuesto


PRECIOS_SERVICIO = {
    'revision_general': 60000,
    'diagnostico_escaner': 99000,
    'cambio_aceite': 280000,
    'mantenimiento_preventivo': 420000,
    'pastillas_freno': 220000,
    'frenos_completo': 480000,
    'alineacion_balanceo': 170000,
    'cambio_bateria': 420000,
    'reparacion_suspension_menor': 250000,
    'reparacion_suspension': 1100000,
    'cambio_amortiguadores': 850000,
    'sincronizacion_motor': 320000,
    'correa_reparticion': 750000,
    'kit_embrague': 1250000,
    'aire_acondicionado': 220000,
    'cambio_llantas': 180000,
    'reparacion_electrica': 180000,
    'reparacion_motor': 1800000,
}


PARTES_SERVICIO = {
    'revision_general': [
        'Filtros', 'bombillos', 'fusibles',
        'limpiaparabrisas', 'niveles de fluidos',
    ],
    'diagnostico_escaner': [
        'Sensores', 'bobinas', 'bujias',
        'fusibles', 'arneses electricos',
    ],
    'cambio_aceite': [
        'Aceite de motor', 'filtro de aceite', 'arandela de carter',
    ],
    'mantenimiento_preventivo': [
        'Aceite', 'filtro de aceite', 'filtro de aire',
        'filtro de cabina', 'bujias',
    ],
    'pastillas_freno': [
        'Pastillas de freno', 'liquido de frenos', 'clips o seguros',
    ],
    'frenos_completo': [
        'Pastillas', 'discos', 'bandas', 'campanas', 'liquido de frenos',
    ],
    'alineacion_balanceo': [
        'Valvulas de rin', 'contrapesas', 'terminales si aplica',
    ],
    'cambio_bateria': [
        'Bateria', 'bornes', 'limpiador de terminales',
    ],
    'reparacion_suspension_menor': [
        'Bujes', 'terminales', 'rotulas', 'bieletas',
    ],
    'reparacion_suspension': [
        'Amortiguadores', 'rotulas', 'bujes', 'terminales', 'bieletas',
    ],
    'cambio_amortiguadores': [
        'Amortiguadores', 'bases', 'guardapolvos', 'topes',
    ],
    'sincronizacion_motor': [
        'Bujias', 'filtro de aire', 'limpiador cuerpo de aceleracion',
    ],
    'correa_reparticion': [
        'Correa de reparticion', 'tensor', 'poleas', 'bomba de agua',
    ],
    'kit_embrague': [
        'Disco', 'prensa', 'balinera', 'guaya o cilindro si aplica',
    ],
    'aire_acondicionado': [
        'Gas refrigerante', 'filtro de cabina', 'valvulas', 'o-rings',
    ],
    'cambio_llantas': [
        'Llantas', 'valvulas', 'contrapesas',
    ],
    'reparacion_electrica': [
        'Fusibles', 'reles', 'cableado', 'terminales', 'sensores',
    ],
    'reparacion_motor': [
        'Empaquetadura', 'anillos', 'casquetes', 'bujias', 'filtros',
    ],
}


TEXTAREA_ATTRS = {
    'class': 'form-control gia-textarea',
    'rows': 4,
}


class OrdenForm(forms.ModelForm):
    class Meta:
        model = Orden
        fields = [
            'cliente',
            'vehiculo',
            'mecanico',
            'tipo_servicio',
            'descripcion',
            'falla_reportada',
            'diagnostico',
            'trabajo_a_realizar',
            'prioridad',
            'estado',
            'costo_mano_obra',
            'fecha_ingreso',
            'fecha_salida',
            'observaciones_mecanico',
        ]
        labels = {
            'cliente': 'Cliente',
            'vehiculo': 'Vehiculo',
            'mecanico': 'Mecanico asignado',
            'tipo_servicio': 'Tipo de servicio',
            'descripcion': 'Descripcion del servicio',
            'falla_reportada': 'Falla reportada',
            'diagnostico': 'Diagnostico',
            'trabajo_a_realizar': 'Trabajo a realizar',
            'prioridad': 'Prioridad',
            'estado': 'Estado',
            'costo_mano_obra': 'Costo mano de obra',
            'fecha_ingreso': 'Fecha de ingreso',
            'fecha_salida': 'Fecha de salida',
            'observaciones_mecanico': 'Observaciones del mecanico',
        }
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'vehiculo': forms.Select(attrs={'class': 'form-select'}),
            'mecanico': forms.Select(attrs={'class': 'form-select'}),
            'tipo_servicio': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={
                **TEXTAREA_ATTRS,
                'placeholder': 'Informacion adicional (opcional)',
            }),
            'falla_reportada': forms.Textarea(attrs={
                **TEXTAREA_ATTRS,
                'placeholder': 'Falla indicada por el cliente (opcional)',
            }),
            'diagnostico': forms.Textarea(attrs={
                **TEXTAREA_ATTRS,
                'placeholder': 'Diagnostico tecnico (opcional)',
            }),
            'trabajo_a_realizar': forms.Textarea(attrs={
                **TEXTAREA_ATTRS,
                'placeholder': 'Trabajo que se debe realizar (opcional)',
            }),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'costo_mano_obra': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
            }),
            'fecha_ingreso': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'fecha_salida': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'observaciones_mecanico': forms.Textarea(attrs={
                **TEXTAREA_ATTRS,
                'rows': 3,
                'placeholder': 'Observaciones del trabajo (opcional)',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mecanico'].required = False
        self.fields['mecanico'].empty_label = 'Sin asignar'

        for name in [
            'descripcion',
            'falla_reportada',
            'diagnostico',
            'trabajo_a_realizar',
            'observaciones_mecanico',
        ]:
            self.fields[name].required = False

    def clean_costo_mano_obra(self):
        costo = self.cleaned_data.get('costo_mano_obra')

        if costo is not None and costo < 0:
            raise forms.ValidationError(
                'El costo del servicio no puede ser negativo.'
            )

        return costo

    def clean(self):
        cleaned_data = super().clean()

        cliente = cleaned_data.get('cliente')
        vehiculo = cleaned_data.get('vehiculo')
        fecha_ingreso = cleaned_data.get('fecha_ingreso')
        fecha_salida = cleaned_data.get('fecha_salida')

        if cliente and vehiculo and vehiculo.cliente_id != cliente.id:
            self.add_error(
                'vehiculo',
                'El vehiculo seleccionado no pertenece al cliente.',
            )

        if (
            fecha_ingreso
            and fecha_salida
            and fecha_salida < fecha_ingreso
        ):
            self.add_error(
                'fecha_salida',
                'La fecha de salida no puede ser anterior a la fecha de ingreso.',
            )

        return cleaned_data


class SolicitudServicioForm(forms.ModelForm):
    class Meta:
        model = Orden
        fields = [
            'vehiculo',
            'tipo_servicio',
            'mecanico',
            'prioridad',
            'descripcion',
            'falla_reportada',
        ]
        labels = {
            'vehiculo': 'Vehiculo',
            'tipo_servicio': 'Tipo de servicio',
            'mecanico': 'Mecanico disponible',
            'prioridad': 'Prioridad',
            'descripcion': 'Descripcion o comentario',
            'falla_reportada': 'Falla reportada',
        }
        widgets = {
            'vehiculo': forms.Select(attrs={'class': 'form-select'}),
            'tipo_servicio': forms.Select(attrs={'class': 'form-select'}),
            'mecanico': forms.Select(attrs={'class': 'form-select'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={
                **TEXTAREA_ATTRS,
                'placeholder': 'Opcional: agrega detalles del servicio...',
            }),
            'falla_reportada': forms.Textarea(attrs={
                **TEXTAREA_ATTRS,
                'placeholder': 'Describe la falla que notas en el vehiculo (opcional)',
            }),
        }

    def __init__(self, *args, cliente=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cliente = cliente

        self.fields['vehiculo'].queryset = (
            cliente.vehiculos.all()
            if cliente
            else self.fields['vehiculo'].queryset.none()
        )
        self.fields['mecanico'].queryset = (
            Mecanico.objects.filter(estado='activo').order_by('nombre')
        )
        self.fields['mecanico'].required = False
        self.fields['mecanico'].empty_label = 'Sin preferencia'
        self.fields['descripcion'].required = False
        self.fields['falla_reportada'].required = False

    def clean_vehiculo(self):
        vehiculo = self.cleaned_data.get('vehiculo')

        if not vehiculo:
            raise forms.ValidationError(
                'Debes seleccionar un vehiculo.'
            )

        if self.cliente and vehiculo.cliente_id != self.cliente.id:
            raise forms.ValidationError(
                'No puedes solicitar servicios para vehiculos de otro cliente.'
            )

        return vehiculo

    def clean_mecanico(self):
        mecanico = self.cleaned_data.get('mecanico')

        if mecanico and mecanico.estado != 'activo':
            raise forms.ValidationError(
                'Selecciona un mecanico activo.'
            )

        return mecanico


class TrabajoMecanicoForm(forms.ModelForm):
    class Meta:
        model = Orden
        fields = [
            'estado',
            'diagnostico',
            'trabajo_a_realizar',
            'costo_mano_obra',
            'observaciones_mecanico',
        ]
        labels = {
            'estado': 'Estado',
            'diagnostico': 'Diagnostico',
            'trabajo_a_realizar': 'Trabajo realizado o por realizar',
            'costo_mano_obra': 'Costo mano de obra',
            'observaciones_mecanico': 'Observaciones o reparaciones realizadas',
        }
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'diagnostico': forms.Textarea(attrs={
                **TEXTAREA_ATTRS,
                'placeholder': 'Diagnostico tecnico (opcional)',
            }),
            'trabajo_a_realizar': forms.Textarea(attrs={
                **TEXTAREA_ATTRS,
                'placeholder': 'Trabajo realizado o pendiente (opcional)',
            }),
            'costo_mano_obra': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
            }),
            'observaciones_mecanico': forms.Textarea(attrs={
                **TEXTAREA_ATTRS,
                'placeholder': 'Puedes escribir alguna observacion (opcional)',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name in [
            'diagnostico',
            'trabajo_a_realizar',
            'observaciones_mecanico',
        ]:
            self.fields[name].required = False

    def clean_costo_mano_obra(self):
        costo = self.cleaned_data.get('costo_mano_obra')

        if costo is not None and costo < 0:
            raise forms.ValidationError(
                'El costo del servicio no puede ser negativo.'
            )

        return costo


class OrdenEstadoForm(TrabajoMecanicoForm):
    pass


class OrdenRepuestoForm(forms.ModelForm):
    # Valida en el servidor que la cantidad sea un entero mayor que cero.
    cantidad = forms.IntegerField(
        min_value=1,
        label='Cantidad',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'step': '1',
        }),
        error_messages={
            'min_value': 'La cantidad debe ser como minimo 1.',
            'invalid': 'Ingresa una cantidad entera valida.',
            'required': 'Debes indicar la cantidad.',
        },
    )

    class Meta:
        model = OrdenRepuesto
        fields = ['repuesto', 'cantidad']
        widgets = {
            'repuesto': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()

        repuesto = cleaned_data.get('repuesto')
        cantidad = cleaned_data.get('cantidad')

        if (
            repuesto
            and cantidad is not None
            and cantidad > repuesto.cantidad_disponible
        ):
            self.add_error(
                'cantidad',
                'No hay stock suficiente.',
            )

        return cleaned_data


class OrdenHerramientaForm(forms.ModelForm):
    class Meta:
        model = OrdenHerramienta
        fields = ['herramienta']
        widgets = {
            'herramienta': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['herramienta'].queryset = (
            self.fields['herramienta'].queryset.filter(
                estado='disponible'
            )
        )

    def clean_herramienta(self):
        herramienta = self.cleaned_data.get('herramienta')

        if herramienta and herramienta.estado != 'disponible':
            raise forms.ValidationError(
                'La herramienta no esta disponible.'
            )

        return herramienta


class EvidenciaOrdenForm(forms.ModelForm):
    class Meta:
        model = EvidenciaOrden
        fields = ['imagen', 'tipo', 'descripcion']
        labels = {
            'imagen': 'Foto de evidencia',
            'tipo': 'Momento del servicio',
            'descripcion': 'Descripcion',
        }
        widgets = {
            'imagen': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'capture': 'environment',
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={
                **TEXTAREA_ATTRS,
                'rows': 3,
                'placeholder': 'Opcional: explica que se ve en la foto...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['descripcion'].required = False

    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')

        if not imagen:
            raise ValidationError(
                'Debes seleccionar una imagen.'
            )

        if imagen.size > 5 * 1024 * 1024:
            raise ValidationError(
                'La imagen no debe superar 5 MB.'
            )

        content_type = getattr(imagen, 'content_type', '')

        if not content_type.startswith('image/'):
            raise ValidationError(
                'Solo se permiten archivos de imagen.'
            )

        return imagen
