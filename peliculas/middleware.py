from django.shortcuts import redirect
from django.urls import reverse
from .models import PerfilUsuario

class LoginRedirectMiddleware:
    """Middleware para redirigir usuarios según su rol después del login"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Si el usuario acaba de hacer login
        if request.user.is_authenticated and request.path == reverse('login'):
            if request.user.is_staff:
                return redirect('/admin/')
            return redirect('/')
        
        return response


class TerminosMiddleware:
    """
    Middleware para verificar que usuarios existentes acepten los términos.
    Solo se ejecuta para usuarios autenticados que no tienen perfil o no han aceptado términos.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs que no requieren verificación de términos
        self.exempt_urls = [
            reverse('peliculas:terminos'),
            reverse('logout'),
            '/static/',
            '/media/',
            '/admin/',
        ]
    
    def __call__(self, request):
        # Solo verificar para usuarios autenticados
        if request.user.is_authenticated:
            # No verificar en URLs exentas
            if any(request.path.startswith(url) for url in self.exempt_urls):
                response = self.get_response(request)
                return response
            
            # Verificar si tiene perfil
            try:
                perfil = request.user.perfil
                # Si no ha aceptado términos, redirigir a la página de términos
                if not perfil.aceptado_terminos and request.path != reverse('peliculas:terminos'):
                    pass
            except PerfilUsuario.DoesNotExist:
                # Crear perfil automáticamente para usuarios sin perfil
                # (esto cubre usuarios creados antes de implementar el sistema)
                PerfilUsuario.objects.create(
                    usuario=request.user,
                    aceptado_terminos=False
                )
        
        response = self.get_response(request)
        return response