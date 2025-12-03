"""
Configuración de URLs para el proyecto AkaFilms.

Este módulo define el enrutamiento principal de URLs del proyecto, incluyendo:
- Panel de administración de Django
- Sistema de autenticación (login/logout)
- Inclusión de URLs de la aplicación 'peliculas'
- Configuración para servir archivos estáticos y media en desarrollo

El sistema de autenticación está centralizado aquí para evitar conflictos
entre rutas de usuario y administrador, utilizando las vistas genéricas
de Django (LoginView, LogoutView).
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Ruta: /admin/
    # Proporciona acceso al panel de administración de Django
    # Requiere usuario con permisos de staff/superuser
    path('login/', auth_views.LoginView.as_view(
        template_name='peliculas/login.html',
        redirect_authenticated_user=True,
        # Redirige según el tipo de usuario después del login
        extra_context={'next': None}
    ), name='login'),
    
    # Ruta: /logout/
    # Vista de cierre de sesión usando LogoutView genérica de Django
    path('logout/', auth_views.LogoutView.as_view(
        next_page='/'
    ), name='logout'),
    
    # Ruta: / (raíz y todas las sub-rutas de peliculas)
    # Incluye todas las URLs definidas en peliculas/urls.py
    path('', include('peliculas.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)