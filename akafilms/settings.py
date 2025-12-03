"""
Django settings para el proyecto AkaFilms.

Este archivo contiene la configuración principal de nuestro proyecto AkaFilms.

Variables de entorno requeridas (.env):
    SECRET_KEY: Clave secreta de Django (str)
    DEBUG: Modo de depuración (bool, default=False)
    ALLOWED_HOSTS: Hosts permitidos separados por coma (str)
"""

from pathlib import Path
import os
from decouple import config, Csv

# CONFIGURACIÓN DE RUTAS

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Clave secreta para firmas criptográficas. que esta configurada en .env
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
# Modo debug. Desactivar en producción (DEBUG=False en .env)
DEBUG = config("DEBUG", default=False, cast=bool)

# Hosts/dominios permitidos para servir la aplicación
# definido en .env en ALLOWED_HOSTS=127.0.0.1,localhost
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())


# DEFINICIÓN DE APLICACIONES

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin', # Panel de administración
    'django.contrib.auth', # Sistema de autenticación
    'django.contrib.contenttypes', # Framework de tipos de contenido
    'django.contrib.sessions', # Manejo de sesiones
    'django.contrib.messages', # Framework de mensajes
    'django.contrib.staticfiles', # Manejo de archivos estáticos
    'peliculas',  # Nuestra aplicación
]



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Middlewares personalizados
    'peliculas.middleware.LoginRedirectMiddleware',  # Redirección automática de usuarios autenticados
    'peliculas.middleware.TerminosMiddleware',       # Verificación de aceptación de términos y condiciones
]

ROOT_URLCONF = 'akafilms.urls'

# CONFIGURACIÓN DE TEMPLATES

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True, # Buscar templates en carpeta 'templates' de cada app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'akafilms.wsgi.application'

# CONFIGURACIÓN DE BASE DE DATOS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# VALIDACIÓN DE CONTRASEÑAS
AUTH_PASSWORD_VALIDATORS = [
    {   # Evita contraseñas similares a atributos del usuario
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', 
    },
    {   # Requiere longitud mínima (default: 8 caracteres)
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {   # Rechaza contraseñas comunes
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {   # Evita contraseñas completamente numéricas
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# CONFIGURACIÓN INTERNACIONAL Y DE ZONA HORARIA
LANGUAGE_CODE = 'es-mx' # Idioma por defecto: Español de México
TIME_ZONE = 'America/Mexico_City' # Zona horaria: Ciudad de México (UTC-6/-5)
USE_I18N = True # Habilitar internacionalización
USE_TZ = True # Usar fechas con zona horaria


# ARCHIVOS ESTÁTICOS Y MEDIA (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Archivos subidos por usuarios (imágenes de perfil, pósters, etc.)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# CONFIGURACIÓN DE MODELOS

# Tipo de campo por defecto para claves primarias
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CONFIGURACIÓN DE SEGURIDAD ADICIONAL

# Habilita filtro XSS del navegador
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True


# Configuración de redirección después del login
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/'  # Por defecto va al inicio

# Configuración de redirección después del logout
LOGOUT_REDIRECT_URL = '/' # Por defecto va al inicio

# Función personalizada para redirigir según tipo de usuario
def login_redirect(request):
    if request.user.is_staff:
        return '/admin/'  # Admins van al panel de administración
    return '/'  # Usuarios normales van al inicio