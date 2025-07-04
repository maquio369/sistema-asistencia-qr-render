from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Invitado


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario',
            'required': True
        }),
        label='Usuario'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'required': True
        }),
        label='Contraseña'
    )


class InvitadoForm(forms.ModelForm):
    class Meta:
        model = Invitado
        fields = ['nombre_completo', 'puesto_cargo', 'fotografia']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del invitado',
                'required': True
            }),
            'puesto_cargo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cargo o puesto que desempeña',
                'required': True
            }),
            'fotografia': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'required': True
            })
        }
        labels = {
            'nombre_completo': 'Nombre Completo',
            'puesto_cargo': 'Puesto o Cargo',
            'fotografia': 'Fotografía del Invitado'
        }
        help_texts = {
            'fotografia': 'Sube una foto clara del invitado (JPG, PNG, etc.)'
        }

    def clean_nombre_completo(self):
        nombre = self.cleaned_data.get('nombre_completo')
        if nombre:
            nombre = nombre.strip().title()
            if len(nombre) < 3:
                raise forms.ValidationError("El nombre debe tener al menos 3 caracteres.")
        return nombre

    def clean_puesto_cargo(self):
        puesto = self.cleaned_data.get('puesto_cargo')
        if puesto:
            puesto = puesto.strip().title()
            if len(puesto) < 2:
                raise forms.ValidationError("El puesto debe tener al menos 2 caracteres.")
        return puesto

    def clean_fotografia(self):
        foto = self.cleaned_data.get('fotografia')
        if foto:
            # Validar tamaño del archivo (máximo 5MB)
            if foto.size > 5 * 1024 * 1024:
                raise forms.ValidationError("La imagen no puede superar los 5MB.")
            
            # Validar tipo de archivo
            if not foto.content_type.startswith('image/'):
                raise forms.ValidationError("Solo se permiten archivos de imagen.")
        
        return foto