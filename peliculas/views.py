from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from .models import Pelicula, Genero, Resena, Calificacion

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