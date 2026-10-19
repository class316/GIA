from django import forms
from django.contrib.auth.password_validation import validate_password

from .models import Usuario


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        label='Contrasena',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Usa una contrasena segura.',
    )

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'rol', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_password(self):
        password = self.cleaned_data['password']
        validate_password(password)
        return password

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['password'])
        usuario.is_staff = usuario.rol == 'admin'
        if commit:
            usuario.save()
            self.save_m2m()
        return usuario


class UsuarioEditarForm(forms.ModelForm):
    password = forms.CharField(
        label='Nueva contrasena',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Dejala en blanco para conservar la actual.',
    )

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'rol', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            validate_password(password, self.instance)
        return password

    def save(self, commit=True):
        usuario = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            usuario.set_password(password)
        usuario.is_staff = usuario.rol == 'admin'
        if commit:
            usuario.save()
            self.save_m2m()
        return usuario
