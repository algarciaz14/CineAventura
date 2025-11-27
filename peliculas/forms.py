from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Pelicula, Genero, Director, Actor, Mensaje, WatchParty
from django.utils import timezone


class RegistroUsuarioForm(UserCreationForm):
    """Formulario de registro con términos y condiciones"""
    email = forms.EmailField(
        required=True,
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Tu nombre'
        })
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        label='Apellido',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Tu apellido'
        })
    )
    
    # Campo para aceptar términos y condiciones
    aceptar_terminos = forms.BooleanField(
        required=True,
        label='',
        error_messages={'required': 'Debes aceptar los términos y condiciones para continuar.'},
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox',
            'id': 'terminos-checkbox'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'aceptar_terminos')
        labels = {
            'username': 'Nombre de usuario',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Elige un nombre de usuario único'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Crea una contraseña segura'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirma tu contraseña'
        })
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'
        
        # Mensajes de ayuda personalizados
        self.fields['username'].help_text = 'Este será tu identificador único. Solo letras, números y @/./+/-/_'
        self.fields['password1'].help_text = 'Mínimo 8 caracteres'
        self.fields['password2'].help_text = None
    
    def clean_email(self):
        """Validar que el email sea único"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este correo electrónico ya está registrado.')
        return email
    
    def clean_username(self):
        """Validar que el username sea único"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Este nombre de usuario ya está en uso.')
        return username
        
    def save(self, commit=True):
        """Guardar el usuario con nombre completo y perfil"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Crear perfil con términos aceptados
            from .models import PerfilUsuario
            PerfilUsuario.objects.create(
                usuario=user,
                aceptado_terminos=True,
                fecha_aceptacion_terminos=timezone.now(),
                version_terminos='1.0'
            )
        return user


class PeliculaForm(forms.ModelForm):
    """Formulario para crear y editar películas"""
    titulo = forms.CharField(
        max_length=300,
        required=True,
        label='Título',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Título de la película'
        })
    )
    titulo_original = forms.CharField(
        max_length=300,
        required=False,
        label='Título Original',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Título original (opcional)'
        })
    )
    sinopsis = forms.CharField(
        required=True,
        label='Sinopsis',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Sinopsis de la película'
        })
    )
    año = forms.IntegerField(
        required=True,
        label='Año de Estreno',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1888,
            'max': 2030,
            'placeholder': 'Año de estreno'
        })
    )
    fecha_estreno = forms.DateField(
        required=True,
        label='Fecha de Estreno',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    duracion = forms.IntegerField(
        required=True,
        label='Duración (minutos)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'max': 400,
            'placeholder': 'Duración en minutos'
        })
    )
    generos = forms.ModelMultipleChoiceField(
        queryset=Genero.objects.all(),
        required=True,
        label='Géneros',
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    director = forms.ModelChoiceField(
        queryset=Director.objects.all().order_by('nombre'),
        required=True,
        label='Director',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    actores = forms.ModelMultipleChoiceField(
        queryset=Actor.objects.all().order_by('nombre'),
        required=False,
        label='Actores',
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    pais = forms.CharField(
        max_length=100,
        required=True,
        label='País',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'País de origen'
        })
    )
    idioma = forms.CharField(
        max_length=100,
        required=True,
        label='Idioma',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Idioma original'
        })
    )
    poster = forms.URLField(
        required=False,
        label='URL del Poster',
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://ejemplo.com/poster.jpg'
        })
    )
    trailer = forms.URLField(
        required=False,
        label='URL del Trailer',
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://youtube.com/watch?v=...'
        })
    )
    presupuesto = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        label='Presupuesto (USD)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Presupuesto en USD'
        })
    )
    recaudacion = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        label='Recaudación (USD)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Recaudación mundial en USD'
        })
    )
    clasificacion = forms.ChoiceField(
        choices=[
            ('G', 'G - Público General'),
            ('PG', 'PG - Se sugiere orientación parental'),
            ('PG-13', 'PG-13 - Mayores de 13 años'),
            ('R', 'R - Restringida'),
            ('NC-17', 'NC-17 - Solo adultos'),
        ],
        required=True,
        label='Clasificación',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = Pelicula
        fields = [
            'titulo', 'titulo_original', 'sinopsis', 'año', 'duracion',
            'generos', 'director', 'actores', 'pais', 'idioma', 'poster',
            'trailer', 'fecha_estreno', 'presupuesto', 'recaudacion',
            'clasificacion',
        ]
    
    def clean_año(self):
        """Validar que el año sea razonable"""
        año = self.cleaned_data.get('año')
        if año < 1888:
            raise ValidationError('El año no puede ser anterior a 1888.')
        if año > 2030:
            raise ValidationError('El año no puede ser mayor a 2030.')
        return año
    
    def clean_duracion(self):
        """Validar que la duración sea razonable"""
        duracion = self.cleaned_data.get('duracion')
        if duracion < 1:
            raise ValidationError('La duración debe ser al menos 1 minuto.')
        if duracion > 400:
            raise ValidationError('La duración no puede ser mayor a 400 minutos.')
        return duracion


class MensajeForm(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Escribe tu mensaje...'
            })
        }
    
    class Meta:
        model = Mensaje
        fields = ['contenido']


class WatchPartyForm(forms.ModelForm):
    """Formulario para crear Watch Parties"""
    nombre = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de tu Watch Party'
        })
    )
    descripcion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Descripción opcional'
        })
    )
    fecha_programada = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        label='Fecha y Hora'
    )
    publico = forms.BooleanField(
        required=False,
        label='Watch Party Público',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    max_participantes = forms.IntegerField(
        initial=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 2,
            'max': 50
        }),
        label='Máximo de Participantes'
    )
    
    class Meta:
        model = WatchParty
        fields = ['nombre', 'descripcion', 'fecha_programada', 'publico', 'max_participantes']
    
    def clean_fecha_programada(self):
        """Validar que la fecha sea futura"""
        fecha = self.cleaned_data.get('fecha_programada')
        if fecha and fecha < timezone.now():
            raise ValidationError('La fecha debe ser en el futuro.')
        return fecha