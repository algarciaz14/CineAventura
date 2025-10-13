"""
URL configuration for akafilms project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Sistema de autenticación unificado
    path('login/', auth_views.LoginView.as_view(
        template_name='peliculas/login.html',
        redirect_authenticated_user=True,
        # Redirige según el tipo de usuario después del login
        extra_context={'next': None}
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(
        next_page='/'
    ), name='logout'),
    
    # URLs de la aplicación
    path('', include('peliculas.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)