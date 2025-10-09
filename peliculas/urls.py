from django.urls import path
from . import views

app_name = 'peliculas'

urlpatterns = [
    path('', views.index, name='index'),
    path('pelicula/<int:pelicula_id>/', views.detalle_pelicula, name='detalle'),
    path('genero/<int:genero_id>/', views.peliculas_por_genero, name='por_genero'),
    path('buscar/', views.buscar, name='buscar'),
    path('pelicula/<int:pelicula_id>/calificar/', views.agregar_calificacion, name='agregar_calificacion'),
    path('pelicula/<int:pelicula_id>/resenar/', views.agregar_resena, name='agregar_resena'),
    path('sobre-nosotros/', views.sobre_nosotros, name='sobre_nosotros'),  # NUEVA LÍNEA
]