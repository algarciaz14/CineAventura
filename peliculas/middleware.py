from django.shortcuts import redirect
from django.urls import reverse

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