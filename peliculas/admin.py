from django.contrib import admin
from .models import (
    Genero, Director, Actor, Pelicula, 
    Calificacion, Resena, ListaPersonalizada
)

@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']

@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'nacionalidad', 'fecha_nacimiento']
    search_fields = ['nombre', 'nacionalidad']
    list_filter = ['nacionalidad']

@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'nacionalidad', 'fecha_nacimiento']
    search_fields = ['nombre', 'nacionalidad']
    list_filter = ['nacionalidad']

@admin.register(Pelicula)
class PeliculaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'año', 'director', 'duracion', 'clasificacion', 'calificacion_promedio']
    search_fields = ['titulo', 'titulo_original', 'sinopsis']
    list_filter = ['año', 'generos', 'clasificacion', 'pais']
    filter_horizontal = ['generos', 'actores']
    date_hierarchy = 'fecha_estreno'
    readonly_fields = ['fecha_agregada', 'actualizada']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'titulo_original', 'sinopsis', 'año', 'duracion')
        }),
        ('Equipo Creativo', {
            'fields': ('director', 'actores')
        }),
        ('Clasificación', {
            'fields': ('generos', 'clasificacion')
        }),
        ('Detalles de Producción', {
            'fields': ('pais', 'idioma', 'fecha_estreno', 'presupuesto', 'recaudacion')
        }),
        ('Multimedia', {
            'fields': ('poster', 'trailer')
        }),
        ('Metadatos', {
            'fields': ('fecha_agregada', 'actualizada'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ['pelicula', 'usuario', 'puntuacion', 'fecha']
    search_fields = ['pelicula__titulo', 'usuario__username']
    list_filter = ['puntuacion', 'fecha']
    date_hierarchy = 'fecha'

@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'pelicula', 'usuario', 'fecha', 'util_count']
    search_fields = ['titulo', 'contenido', 'pelicula__titulo', 'usuario__username']
    list_filter = ['fecha']
    date_hierarchy = 'fecha'
    readonly_fields = ['fecha', 'actualizada']

@admin.register(ListaPersonalizada)
class ListaPersonalizadaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'usuario', 'publica', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion', 'usuario__username']
    list_filter = ['publica', 'fecha_creacion']
    filter_horizontal = ['peliculas']
    date_hierarchy = 'fecha_creacion'