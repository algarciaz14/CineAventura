from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils import timezone

class Genero(models.Model):
    """Modelo para los géneros cinematográficos"""
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Género"
        verbose_name_plural = "Géneros"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Director(models.Model):
    """Modelo para directores de películas"""
    nombre = models.CharField(max_length=200)
    biografia = models.TextField(blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    nacionalidad = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = "Director"
        verbose_name_plural = "Directores"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Actor(models.Model):
    """Modelo para actores"""
    nombre = models.CharField(max_length=200)
    biografia = models.TextField(blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    nacionalidad = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = "Actor"
        verbose_name_plural = "Actores"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Pelicula(models.Model):
    """Modelo principal para películas"""
    titulo = models.CharField(max_length=300)
    titulo_original = models.CharField(max_length=300, blank=True)
    sinopsis = models.TextField()
    año = models.IntegerField(
        validators=[MinValueValidator(1888), MaxValueValidator(2030)]
    )
    duracion = models.IntegerField(help_text="Duración en minutos")
    generos = models.ManyToManyField(Genero, related_name='peliculas')
    director = models.ForeignKey(
        Director, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='peliculas'
    )
    actores = models.ManyToManyField(Actor, related_name='peliculas', blank=True)
    pais = models.CharField(max_length=100)
    idioma = models.CharField(max_length=100)
    poster = models.URLField(blank=True, help_text="URL del poster de la película")
    trailer = models.URLField(blank=True, help_text="URL del trailer (YouTube)")
    fecha_estreno = models.DateField()
    presupuesto = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Presupuesto en USD"
    )
    recaudacion = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Recaudación mundial en USD"
    )
    clasificacion = models.CharField(
        max_length=10,
        choices=[
            ('G', 'G - Público General'),
            ('PG', 'PG - Se sugiere orientación parental'),
            ('PG-13', 'PG-13 - Mayores de 13 años'),
            ('R', 'R - Restringida'),
            ('NC-17', 'NC-17 - Solo adultos'),
        ],
        default='PG-13'
    )
    fecha_agregada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Película"
        verbose_name_plural = "Películas"
        ordering = ['-año', 'titulo']
    
    def __str__(self):
        return f"{self.titulo} ({self.año})"
    
    def calificacion_promedio(self):
        """Calcula la calificación promedio de la película"""
        calificaciones = self.calificaciones.all()
        if calificaciones:
            return round(sum(c.puntuacion for c in calificaciones) / len(calificaciones), 1)
        return 0
    
    def total_resenas(self):
        """Retorna el total de reseñas"""
        return self.resenas.count()

class Calificacion(models.Model):
    """Modelo para calificaciones de usuarios"""
    pelicula = models.ForeignKey(
        Pelicula, 
        on_delete=models.CASCADE, 
        related_name='calificaciones'
    )
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='calificaciones'
    )
    puntuacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Calificación"
        verbose_name_plural = "Calificaciones"
        unique_together = ['pelicula', 'usuario']
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.pelicula.titulo}: {self.puntuacion}/10"

class Resena(models.Model):
    """Modelo para reseñas de usuarios"""
    pelicula = models.ForeignKey(
        Pelicula, 
        on_delete=models.CASCADE, 
        related_name='resenas'
    )
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='resenas'
    )
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)
    util_count = models.IntegerField(default=0, help_text="Votos de utilidad")
    
    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        unique_together = ['pelicula', 'usuario']
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.pelicula.titulo}"

class ListaPersonalizada(models.Model):
    """Modelo para listas personalizadas de usuarios"""
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='listas'
    )
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    peliculas = models.ManyToManyField(Pelicula, related_name='en_listas', blank=True)
    publica = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Lista Personalizada"
        verbose_name_plural = "Listas Personalizadas"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.nombre} - {self.usuario.username}"