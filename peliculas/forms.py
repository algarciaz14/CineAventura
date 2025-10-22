from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import *

class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
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
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        labels = {
            'username': 'Nombre de usuario',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Elige un nombre de usuario'
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
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user
    
from django import forms
from django.core.exceptions import ValidationError
from .models import Pelicula, Genero, Director, Actor


class PeliculaForm(forms.ModelForm):
    """Formulario para crear y editar películas"""
    titulo = forms.CharField(
        max_length=300,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Título de la película'
        })
    )
    titulo_original = forms.CharField(
        max_length=300,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Título original (opcional)'
        })
    )
    sinopsis = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Sinopsis de la película'
        })
    )
    anio = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1888,
            'max': 2030,
            'placeholder': 'Año de estreno'
        })
    )
    fecha_estreno = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type':'date'
        })
    )
    duracion = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'max': 400,
            'placeholder':'Duración en minutos'
        })
    )
    generos = forms.ModelMultipleChoiceField(
        queryset=Genero.objects.all(),
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    director = forms.ModelMultipleChoiceField(
        queryset=Director.objects.all().order_by('nombre'),
        required=False,
        widget=forms.Select(attrs={
                'class': 'form-control'
        })
    )
    actores = forms.ModelMultipleChoiceField(
        queryset=Actor.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    pais = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder':'País de origen'
        })
    )
    idioma = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder':'Idioma original'
        })
    )
    poster = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder':'https://ejemplo.com/poster.jpg'
        })
    )
    trailer = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder':'https://youtube.com/watch?v=...'
        })
    )
    presupuesto = forms.DecimalField(
        max_digits=15,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder':'Presupuesto en USD'
        })
    )
    recaudacion = forms.DecimalField(
        max_digits=15,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder':'Recaudación mundial en USD'
        })
    )
    clasificacion = forms.MultipleChoiceField(
        choices=[
            ('G', 'G - Público General'),
            ('PG', 'PG - Se sugiere orientación parental'),
            ('PG-13', 'PG-13 - Mayores de 13 años'),
            ('R', 'R - Restringida'),
            ('NC-17', 'NC-17 - Solo adultos'),
        ],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
    )
    class Meta:
        model = Pelicula
        fields = [
            'titulo',
            'titulo_original',
            'sinopsis',
            'anio',
            'duracion',
            'generos',
            'director',
            'actores',
            'pais',
            'idioma',
            'poster',
            'trailer',
            'fecha_estreno',
            'presupuesto',
            'recaudacion',
            'clasificacion',
        ]
        
        labels = {
            'titulo': 'Título',
            'titulo_original': 'Título Original',
            'sinopsis': 'Sinopsis',
            'anio': 'Año de Estreno',
            'duracion': 'Duración (minutos)',
            'generos': 'Géneros',
            'director': 'Director',
            'actores': 'Actores',
            'pais': 'País',
            'idioma': 'Idioma',
            'poster': 'URL del Poster',
            'trailer': 'URL del Trailer',
            'fecha_estreno': 'Fecha de Estreno',
            'presupuesto': 'Presupuesto (USD)',
            'recaudacion': 'Recaudación (USD)',
            'clasificacion': 'Clasificación',
        }
    
    # Validaciones adicionales