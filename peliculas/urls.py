from django.urls import path
from . import views

app_name = 'peliculas'

urlpatterns = [
    path('', views.index, name='index'),
    path('registro/', views.registro, name='registro'),  # NUEVA
    path('perfil/', views.mi_perfil, name='perfil'),  # NUEVA
    path('pelicula/<int:pelicula_id>/', views.detalle_pelicula, name='detalle'),
    path('genero/<int:genero_id>/', views.peliculas_por_genero, name='por_genero'),
    path('buscar/', views.buscar, name='buscar'),
    path('pelicula/<int:pelicula_id>/calificar/', views.agregar_calificacion, name='agregar_calificacion'),
    path('pelicula/<int:pelicula_id>/resenar/', views.agregar_resena, name='agregar_resena'),
    path('pelicula/<int:pelicula_id>/favoritos/', views.agregar_favoritos, name='agregar_favoritos'),  # NUEVA
    path('pelicula/<int:pelicula_id>/ver-despues/', views.agregar_ver_despues, name='agregar_ver_despues'),  # NUEVA
    path('sobre-nosotros/', views.sobre_nosotros, name='sobre_nosotros'),
    path('nueva-pelicula/', views.nueva_pelicula, name='nueva_pelicula'),
]