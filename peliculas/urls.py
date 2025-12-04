from django.urls import path
from . import views

app_name = 'peliculas'

urlpatterns = [
    # Rutas básicas
    path('', views.index, name='index'),
    path('registro/', views.registro, name='registro'),
    path('perfil/', views.mi_perfil, name='perfil'),
    path('pelicula/<int:pelicula_id>/', views.detalle_pelicula, name='detalle'),
    path('genero/<int:genero_id>/', views.peliculas_por_genero, name='por_genero'),
    path('buscar/', views.buscar, name='buscar'),
    path('sobre-nosotros/', views.sobre_nosotros, name='sobre_nosotros'),
    path('nueva-pelicula/', views.nueva_pelicula, name='nueva_pelicula'),
    
    # Terminos y condiciones
    path('terminos/', views.terminos_condiciones, name='terminos'),
    
    # Interacciones con pelÃ­culas
    path('pelicula/<int:pelicula_id>/calificar/', views.agregar_calificacion, name='agregar_calificacion'),
    path('pelicula/<int:pelicula_id>/resenar/', views.agregar_resena, name='agregar_resena'),
    path('pelicula/<int:pelicula_id>/favoritos/', views.agregar_favoritos, name='agregar_favoritos'),
    path('pelicula/<int:pelicula_id>/ver-despues/', views.agregar_ver_despues, name='agregar_ver_despues'),
    
    
    # Sistema de mensajeria
    path('mensajes/', views.lista_conversaciones, name='lista_conversaciones'),
    path('mensajes/<int:conversacion_id>/', views.conversacion, name='conversacion'),
    path('mensajes/nueva/<int:usuario_id>/', views.nueva_conversacion, name='nueva_conversacion'),
    
    path('social-hub/', views.social_hub, name='social_hub'),
    path('usuario/<int:usuario_id>/', views.perfil_usuario, name='perfil_usuario'),
    path('mensajes/no-leidos/json/', views.mensajes_no_leidos_json, name='mensajes_no_leidos_json'),

    
    # Notificaciones
    path('notificaciones/', views.notificaciones, name='notificaciones'),
    path('notificaciones/json/', views.notificaciones_json, name='notificaciones_json'),
    
    # Recomendaciones
    path('recomendaciones/', views.recomendaciones_view, name='recomendaciones'),
    
    # Watch Parties
    path('watch-parties/', views.lista_watch_parties, name='lista_watch_parties'),
    path('watch-parties/crear/<int:pelicula_id>/', views.crear_watch_party, name='crear_watch_party'),
    path('watch-parties/<int:party_id>/', views.detalle_watch_party, name='detalle_watch_party'),
    path('watch-parties/<int:party_id>/unirse/', views.unirse_watch_party, name='unirse_watch_party'),
    path('watch-parties/<int:party_id>/salir/', views.salir_watch_party, name='salir_watch_party'),
    path('watch-parties/<int:party_id>/mensaje/', views.enviar_mensaje_watch_party, name='enviar_mensaje_watch_party'),
    
    path('catalogo/', views.catalogo_completo, name='catalogo'),
    # Integración TMDB
path('tmdb/buscar/', views.buscar_tmdb, name='buscar_tmdb'),
path('tmdb/importar/<int:tmdb_id>/', views.importar_pelicula_tmdb, name='importar_tmdb'),
]