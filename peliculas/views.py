from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from .models import Pelicula, Genero, Resena, Calificacion
from django.contrib.auth import login, authenticate
from .forms import *

def index(request):
    """Vista principal - Página de inicio"""
    # Películas destacadas (mejor calificadas)
    peliculas_destacadas = Pelicula.objects.annotate(
        promedio=Avg('calificaciones__puntuacion')
    ).order_by('-promedio')[:6]
    
    # Películas recientes
    peliculas_recientes = Pelicula.objects.order_by('-fecha_agregada')[:6]
    
    # Géneros disponibles
    generos = Genero.objects.all()
    
    context = {
        'peliculas_destacadas': peliculas_destacadas,
        'peliculas_recientes': peliculas_recientes,
        'generos': generos,
    }
    return render(request, 'peliculas/index.html', context)

def detalle_pelicula(request, pelicula_id):
    """Vista de detalle de una película"""
    pelicula = get_object_or_404(Pelicula, pk=pelicula_id)
    
    # Obtener reseñas
    resenas = pelicula.resenas.select_related('usuario').order_by('-fecha')[:10]
    
    # Calificación del usuario actual (si está autenticado)
    calificacion_usuario = None
    if request.user.is_authenticated:
        try:
            calificacion_usuario = Calificacion.objects.get(
                pelicula=pelicula, 
                usuario=request.user
            )
        except Calificacion.DoesNotExist:
            pass
    
    context = {
        'pelicula': pelicula,
        'resenas': resenas,
        'calificacion_usuario': calificacion_usuario,
        'range_10': range(1, 11),
    }
    return render(request, 'peliculas/detalle.html', context)

def peliculas_por_genero(request, genero_id):
    """Vista de películas filtradas por género"""
    genero = get_object_or_404(Genero, pk=genero_id)
    peliculas_list = Pelicula.objects.filter(generos=genero).annotate(
        promedio=Avg('calificaciones__puntuacion')
    ).order_by('-promedio')
    
    # Paginación
    paginator = Paginator(peliculas_list, 12)
    page_number = request.GET.get('page')
    peliculas = paginator.get_page(page_number)
    
    context = {
        'genero': genero,
        'peliculas': peliculas,
    }
    return render(request, 'peliculas/por_genero.html', context)

def buscar(request):
    """Vista de búsqueda de películas"""
    query = request.GET.get('q', '')
    peliculas = []
    
    if query:
        peliculas = Pelicula.objects.filter(
            Q(titulo__icontains=query) |
            Q(titulo_original__icontains=query) |
            Q(sinopsis__icontains=query) |
            Q(director__nombre__icontains=query) |
            Q(actores__nombre__icontains=query)
        ).distinct().annotate(
            promedio=Avg('calificaciones__puntuacion')
        ).order_by('-promedio')
    
    context = {
        'query': query,
        'peliculas': peliculas,
    }
    return render(request, 'peliculas/buscar.html', context)

@login_required
def agregar_calificacion(request, pelicula_id):
    """Vista para agregar o actualizar calificación"""
    if request.method == 'POST':
        pelicula = get_object_or_404(Pelicula, pk=pelicula_id)
        puntuacion = int(request.POST.get('puntuacion', 0))
        
        if 1 <= puntuacion <= 10:
            calificacion, created = Calificacion.objects.update_or_create(
                pelicula=pelicula,
                usuario=request.user,
                defaults={'puntuacion': puntuacion}
            )
            
            if created:
                messages.success(request, '¡Calificación agregada exitosamente!')
            else:
                messages.success(request, '¡Calificación actualizada!')
        else:
            messages.error(request, 'La calificación debe estar entre 1 y 10.')
    
    return redirect('peliculas:detalle', pelicula_id=pelicula_id)

@login_required
def agregar_resena(request, pelicula_id):
    """Vista para agregar reseña"""
    if request.method == 'POST':
        pelicula = get_object_or_404(Pelicula, pk=pelicula_id)
        titulo = request.POST.get('titulo', '')
        contenido = request.POST.get('contenido', '')
        
        if titulo and contenido:
            resena, created = Resena.objects.update_or_create(
                pelicula=pelicula,
                usuario=request.user,
                defaults={
                    'titulo': titulo,
                    'contenido': contenido
                }
            )
            
            if created:
                messages.success(request, '¡Reseña publicada exitosamente!')
            else:
                messages.success(request, '¡Reseña actualizada!')
        else:
            messages.error(request, 'Debes completar todos los campos.')
    
    return redirect('peliculas:detalle', pelicula_id=pelicula_id)

def sobre_nosotros(request):
    """Vista de la página Sobre Nosotros"""
    return render(request, 'peliculas/sobre_nosotros.html')

def registro(request):
    """Vista de registro de nuevos usuarios"""
    if request.user.is_authenticated:
        return redirect('peliculas:index')
    
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f'¡Bienvenido {username}! Tu cuenta ha sido creada exitosamente.')
            
            # Redirigir según tipo de usuario
            if user.is_staff:
                return redirect('/admin/')
            return redirect('peliculas:index')
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'peliculas/registro.html', {'form': form})

@login_required
def agregar_favoritos(request, pelicula_id):
    """Agregar/quitar película de favoritos"""
    pelicula = get_object_or_404(Pelicula, pk=pelicula_id)
    
    if request.user.peliculas_favoritas.filter(id=pelicula_id).exists():
        request.user.peliculas_favoritas.remove(pelicula)
        messages.success(request, f'"{pelicula.titulo}" eliminada de tus favoritos.')
    else:
        request.user.peliculas_favoritas.add(pelicula)
        messages.success(request, f'"{pelicula.titulo}" agregada a tus favoritos.')
    
    return redirect('peliculas:detalle', pelicula_id=pelicula_id)

@login_required
def agregar_ver_despues(request, pelicula_id):
    """Agregar/quitar película de ver después"""
    pelicula = get_object_or_404(Pelicula, pk=pelicula_id)
    
    if request.user.peliculas_ver_despues.filter(id=pelicula_id).exists():
        request.user.peliculas_ver_despues.remove(pelicula)
        messages.success(request, f'"{pelicula.titulo}" eliminada de tu lista.')
    else:
        request.user.peliculas_ver_despues.add(pelicula)
        messages.success(request, f'"{pelicula.titulo}" agregada a Ver Después.')
    
    return redirect('peliculas:detalle', pelicula_id=pelicula_id)

@login_required
def mi_perfil(request):
    """Vista del perfil del usuario"""
    favoritos = request.user.peliculas_favoritas.all()
    ver_despues = request.user.peliculas_ver_despues.all()
    mis_calificaciones = Calificacion.objects.filter(usuario=request.user).select_related('pelicula')
    mis_resenas = Resena.objects.filter(usuario=request.user).select_related('pelicula')
    
    context = {
        'favoritos': favoritos,
        'ver_despues': ver_despues,
        'mis_calificaciones': mis_calificaciones,
        'mis_resenas': mis_resenas,
    }
    return render(request, 'peliculas/perfil.html', context)

@login_required
def nueva_pelicula(request):
    """Vista para agregar una nueva película, únicamente para administradores"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('peliculas:index')
    if request.method == 'POST':
        form = PeliculaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Nueva película agregada exitosamente!')
            return redirect('peliculas:index')
        pass
    else:
        form = PeliculaForm()
    return render(request, 'peliculas/nueva_pelicula.html', {'form': form})