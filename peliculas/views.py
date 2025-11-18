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
    
    # Géneros para el navbar
    generos = Genero.objects.all()
    
    context = {
        'pelicula': pelicula,
        'resenas': resenas,
        'calificacion_usuario': calificacion_usuario,
        'range_10': range(1, 11),
        'generos': generos,
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
    
    # Géneros para el navbar
    generos = Genero.objects.all()
    
    context = {
        'genero': genero,
        'peliculas': peliculas,
        'generos': generos,
    }
    return render(request, 'peliculas/por_genero.html', context)

def buscar(request):
    """Vista de búsqueda de películas mejorada con traducciones"""
    query = request.GET.get('q', '').strip()
    peliculas = []
    generos = Genero.objects.all()
    
    # Diccionario de traducciones español -> inglés 
    TRADUCCIONES = {
        # Artículos y palabras comunes
        'el': 'the',
        'la': 'the',
        'los': 'the',
        'las': 'the',
        'un': 'a',
        'una': 'a',
        'de': 'of',
        'del': 'of the',
        'y': 'and',
        
        # Películas específicas en nuestra  base de datos
        'caballero': 'knight',
        'oscuro': 'dark',
        'cuaderno': 'notebook',
        'diario': 'notebook',
        'resaca': 'hangover',
        'piratas': 'pirates',
        'caribe': 'caribbean',
        'gladiador': 'gladiator',
        'jurasico': 'jurassic',
        'parque': 'park',
        'hobbit': 'hobbit',
        'viaje': 'journey',
        'inesperado': 'unexpected',
        'señor': 'lord',
        'anillos': 'rings',
        'comunidad': 'fellowship',
        'anillo': 'ring',
        'harry': 'harry',
        'potter': 'potter',
        'piedra': 'stone',
        'filosofal': "sorcerer's",
        'hechicero': "sorcerer's",
        'laberinto': 'labyrinth',
        'fauno': "pan's",
        'forma': 'shape',
        'agua': 'water',
        'pez': 'fish',
        'grande': 'big',
        'orgullo': 'pride',
        'prejuicio': 'prejudice',
        'tierra': 'land',
        'eterno': 'eternal',
        'resplandor': 'sunshine',
        'mente': 'mind',
        'sin': 'spotless',
        'mancha': 'spotless',
        'inmaculada': 'spotless',
        
        # Términos de títulos comunes
        'origen': 'inception',
        'comienzo': 'inception',
        'interestelar': 'interstellar',
        'llegada': 'arrival',
        'duna': 'dune',
        'corredor': 'runner',
        'hoja': 'blade',
        'redencion': 'redemption',
        'cadena': 'shawshank',
        'perpetua': 'shawshank',
        'milla': 'mile',
        'milagro': 'green mile',
        'mente': 'mind',
        'hermosa': 'beautiful',
        'bella': 'beautiful',
        'salir': 'get out',
        'huir': 'get out',
        'fuera': 'out',
        'conjuro': 'conjuring',
        'invocacion': 'conjuring',
        'lugar': 'place',
        'silencio': 'quiet',
        'silencioso': 'quiet',
        'hereditario': 'hereditary',
        'eso': 'it',
        'payaso': 'it',
        
        # Términos generales
        'guerra': 'war',
        'amor': 'love',
        'muerte': 'death',
        'vida': 'life',
        'rey': 'king',
        'reina': 'queen',
        'principe': 'prince',
        'princesa': 'princess',
        'dragon': 'dragon',
        'noche': 'night',  
        'dia': 'day',
        'ciudad': 'city',
        'mundo': 'world',
        'hombre': 'man',
        'mujer': 'woman',
        'niño': 'boy',
        'niña': 'girl',
        'estrella': 'star',
        'estrellas': 'stars',
        'planeta': 'planet',
        'cielo': 'sky',
        'infierno': 'hell',
        'paraiso': 'paradise',
        'hermano': 'brother',
        'hermanos': 'brothers',
        'hermana': 'sister',
        'familia': 'family',
        'casa': 'house',
        'hogar': 'home',
        'rojo': 'red',
        'azul': 'blue',
        'verde': 'green',
        'negro': 'black',
        'blanco': 'white',
        'secreto': 'secret',
        'misterio': 'mystery',
        'ultimo': 'last',
        'primera': 'first',
        'primer': 'first',
        'nuevo': 'new',
        'viejo': 'old',
        'joven': 'young',
        'pequeño': 'small',
        'loco': 'mad',
        'max': 'max',
        'furia': 'fury',
        'camino': 'road',
        'carretera': 'road',
        'matrix': 'matrix',
        'invasores': 'raiders',
        'arca': 'ark',
        'perdida': 'lost',
        'perdido': 'lost',
        'avatar': 'avatar',
        'titanic': 'titanic',
        'forrest': 'forrest',
        'gump': 'gump',
        'latigo': 'whiplash',
        'damas': 'bridesmaids',
        'honor': 'bridesmaids',
        'hermanastros': 'step brothers',
        'calle': 'street',
        'salto': 'jump',
    }
    
    if query:
        # Ignorar búsquedas muy cortas (menos de 3 caracteres)
        if len(query) < 3:
            context = {
                'query': query,
                'peliculas': peliculas,
                'generos': generos,
                'mensaje_error': 'Por favor ingresa al menos 3 caracteres para buscar.'
            }
            return render(request, 'peliculas/buscar.html', context)
        
        # Limpiar y normalizar el query
        query_limpio = query.strip().lower()
        
        # Crear consulta base
        q_objects = Q()
        
        # 1. SIEMPRE buscar con el texto original primero
        q_objects |= Q(titulo__icontains=query)
        q_objects |= Q(titulo_original__icontains=query)
        
        # 2. Buscar si la frase completa tiene traducción exacta
        if query_limpio in TRADUCCIONES:
            query_traducido = TRADUCCIONES[query_limpio]
            q_objects |= Q(titulo__icontains=query_traducido)
            q_objects |= Q(titulo_original__icontains=query_traducido)
        
        # 3. Traducir palabra por palabra Y buscar cada palabra clave
        palabras = query_limpio.split()
        palabras_importantes = []  # Solo palabras de 4+ caracteres
        
        for palabra in palabras:
            # Traducir si existe
            if palabra in TRADUCCIONES:
                palabra_trad = TRADUCCIONES[palabra]
                # Si la traducción no es un artículo, es importante
                if palabra_trad not in ['the', 'a', 'an', 'of', 'in', 'and']:
                    palabras_importantes.append(palabra_trad)
                    # Buscar cada palabra importante individualmente
                    if len(palabra_trad) >= 4:
                        q_objects |= Q(titulo__icontains=palabra_trad)
                        q_objects |= Q(titulo_original__icontains=palabra_trad)
            elif len(palabra) >= 4:
                # Palabra sin traducción pero suficientemente larga
                palabras_importantes.append(palabra)
                q_objects |= Q(titulo__icontains=palabra)
                q_objects |= Q(titulo_original__icontains=palabra)
        
        # 4. Buscar con la frase completa traducida (palabra por palabra)
        if palabras_importantes:
            query_traducido_completo = ' '.join(palabras_importantes)
            if query_traducido_completo != query_limpio:
                q_objects |= Q(titulo__icontains=query_traducido_completo)
                q_objects |= Q(titulo_original__icontains=query_traducido_completo)
        
        # 5. Buscar en géneros (solo si no es muy corto)
        if len(query) >= 4:
            q_objects |= Q(generos__nombre__icontains=query)
        
        # Ejecutar búsqueda
        peliculas = Pelicula.objects.filter(q_objects).distinct().annotate(
            promedio=Avg('calificaciones__puntuacion')
        ).order_by('-promedio')
    
    context = {
        'query': query,
        'peliculas': peliculas,
        'generos': generos,
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
    generos = Genero.objects.all()
    return render(request, 'peliculas/sobre_nosotros.html', {'generos': generos})

def registro(request):
    """Vista de registro de nuevos usuarios"""
    if request.user.is_authenticated:
        return redirect('peliculas:index')
    
    generos = Genero.objects.all()
    
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
    
    return render(request, 'peliculas/registro.html', {'form': form, 'generos': generos})

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
    
    generos = Genero.objects.all()
    
    context = {
        'favoritos': favoritos,
        'ver_despues': ver_despues,
        'mis_calificaciones': mis_calificaciones,
        'mis_resenas': mis_resenas,
        'generos': generos,
    }
    return render(request, 'peliculas/perfil.html', context)

@login_required
def nueva_pelicula(request):
    """Vista para agregar una nueva película, únicamente para administradores"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('peliculas:index')
    
    generos = Genero.objects.all()
    
    if request.method == 'POST':
        form = PeliculaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Nueva película agregada exitosamente!')
            return redirect('peliculas:index')
    else:
        form = PeliculaForm()
    
    return render(request, 'peliculas/nueva_pelicula.html', {'form': form, 'generos': generos})