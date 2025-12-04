"""
Configuración WSGI para el proyecto AkaFilms.

WSGI (Web Server Gateway Interface) es el estándar de Python para la comunicación
entre servidores web y aplicaciones web. Este archivo expone la aplicación WSGI
como una variable de nivel de módulo llamada ``application``.

Este archivo es utilizado por servidores WSGI compatibles como:
- Gunicorn (recomendado para producción)
- uWSGI
- mod_wsgi (Apache)
- Waitress
- Cualquier servidor compatible con WSGI

Uso en desarrollo:
    El servidor de desarrollo de Django (runserver) NO usa este archivo.
    Este archivo solo es necesario para despliegue en producción.
"""


import os

from django.core.wsgi import get_wsgi_application

# Establece la variable de entorno DJANGO_SETTINGS_MODULE si no está definida
# Esta variable le indica a Django qué archivo de configuración usar
#
# Por defecto apunta a: akafilms.settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cineAventura.settings')

# Obtiene la aplicación WSGI de Django
# Esta es la interfaz entre el servidor web y tu aplicación Django
application = get_wsgi_application()
