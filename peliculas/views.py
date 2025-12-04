from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Prefetch
from collections import Counter
import random
import string

from .models import (
    Pelicula, Genero, Resena, Calificacion, 
    Conversacion, Mensaje, Notificacion,
    HistorialVisualizacion, WatchParty, MensajeWatchParty,
    PerfilUsuario
)
from .forms import (
    RegistroUsuarioForm, PeliculaForm, MensajeForm, WatchPartyForm
)


def index(request):
    """
    Vista principal - Página de inicio.
    
    Muestra películas de AVENTURA destacadas, recientes y recomendaciones personalizadas.
    Las recomendaciones solo aparecen para usuarios autenticados.
    """
    
    # Obtener el género Aventura
    genero_aventura = Genero.objects.filter(nombre__iexact='aventura').first()
    
    # Filtrar solo películas de aventura
    peliculas_aventura = Pelicula.objects.filter(generos=genero_aventura) if genero_aventura else Pelicula.objects.none()
    
    # Películas con mejor calificación promedio (top 6) - SOLO AVENTURA
    peliculas_destacadas = peliculas_aventura.annotate(
        promedio=Avg('calificaciones__puntuacion')
    ).order_by('-promedio')[:5]
    
    # Películas agregadas más recientemente (top 6) - SOLO AVENTURA
    peliculas_recientes = peliculas_aventura.order_by('-fecha_agregada')[:6]
    
    # Obtener todos los géneros para el menú (aunque solo mostramos aventura)
    generos = Genero.objects.all()
    
    # Recomendaciones personalizadas si esta autenticado - SOLO AVENTURA
    recomendaciones = []
    if request.user.is_authenticated:
        recomendaciones = obtener_recomendaciones_aventura(request.user)[:6]
    
    context = {
        'peliculas_destacadas': peliculas_destacadas,
        'peliculas_recientes': peliculas_recientes,
        'recomendaciones': recomendaciones,
        'generos': generos,
        'genero_aventura': genero_aventura,
    }
    return render(request, 'peliculas/index.html', context)

def catalogo_completo(request):
    """
    Vista del catálogo completo de películas con búsqueda y ordenamiento.
    """
    # Obtener el género Aventura
    genero_aventura = Genero.objects.filter(nombre__iexact='aventura').first()
    
    # Filtrar solo películas de aventura
    peliculas_list = Pelicula.objects.filter(generos=genero_aventura) if genero_aventura else Pelicula.objects.all()
    
    # Anotar con calificación promedio
    peliculas_list = peliculas_list.annotate(
        promedio=Avg('calificaciones__puntuacion')
    )
    
    # Búsqueda
    query = request.GET.get('q', '').strip()
    if query:
        peliculas_list = peliculas_list.filter(
            Q(titulo__icontains=query) |
            Q(titulo_original__icontains=query) |
            Q(sinopsis__icontains=query)
        )
    
    # Ordenamiento
    orden = request.GET.get('orden', 'az')
    
    if orden == 'az':
        peliculas_list = peliculas_list.order_by('titulo')
    elif orden == 'za':
        peliculas_list = peliculas_list.order_by('-titulo')
    elif orden == 'reciente':
        peliculas_list = peliculas_list.order_by('-año', '-fecha_agregada')
    elif orden == 'antiguo':
        peliculas_list = peliculas_list.order_by('año', 'fecha_agregada')
    elif orden == 'mejor':
        peliculas_list = peliculas_list.order_by('-promedio', '-año')
    elif orden == 'peor':
        peliculas_list = peliculas_list.order_by('promedio', 'año')
    
    # Paginación: 12 películas por página
    paginator = Paginator(peliculas_list, 12)
    page_number = request.GET.get('page')
    peliculas = paginator.get_page(page_number)
    
    generos = Genero.objects.all()
    
    context = {
        'peliculas': peliculas,
        'query': query,
        'orden': orden,
        'total_peliculas': peliculas_list.count(),
        'generos': generos,
    }
    return render(request, 'peliculas/catalogo.html', context)

def detalle_pelicula(request, pelicula_id):
    """
    Vista de detalle de una película.
    
    Muestra información completa, reseñas, calificación del usuario
    y watch parties próximas. Registra la visualización si el usuario
    está autenticado.
    """
    
    # Obtiene la película o retorna 404 si no existe
    pelicula = get_object_or_404(Pelicula, pk=pelicula_id)
    
    # Registrar visualización si esta autenticado
    # Registrar visualización en el historial del usuario
    if request.user.is_authenticated:
        HistorialVisualizacion.objects.get_or_create(
            usuario=request.user,
            pelicula=pelicula,
            defaults={'fecha_visualizacion': timezone.now()}
        )
    
    # Obtener reseñas con información del usuario (optimización con select_related)
    resenas = pelicula.resenas.select_related('usuario').order_by('-fecha')[:10]
    
    # Verificar si el usuario ya calificó esta película
    calificacion_usuario = None
    if request.user.is_authenticated:
        try:
            calificacion_usuario = Calificacion.objects.get(
                pelicula=pelicula, 
                usuario=request.user
            )
        except Calificacion.DoesNotExist:
            pass
    
    # Obtener géneros para el menú
    generos = Genero.objects.all()
    
    # Watch parties próximas para esta película
    watch_parties_proximas = WatchParty.objects.filter(
        pelicula=pelicula,
        estado='esperando',
        fecha_programada__gte=timezone.now()
    ).order_by('fecha_programada')[:5]
    
    context = {
        'pelicula': pelicula,
        'resenas': resenas,
        'calificacion_usuario': calificacion_usuario,
        'range_10': range(1, 11),
        'generos': generos,
        'watch_parties_proximas': watch_parties_proximas,
    }
    return render(request, 'peliculas/detalle.html', context)


def peliculas_por_genero(request, genero_id):
    """
    Vista de películas filtradas por género.
    
    Muestra todas las películas de un género específico
    ordenadas por calificación promedio con paginación.
    """
    
    # Obtiene el género o retorna 404
    genero = get_object_or_404(Genero, pk=genero_id)
    # Filtra películas por género y calcula promedio de calificaciones
    peliculas_list = Pelicula.objects.filter(generos=genero).annotate(
        promedio=Avg('calificaciones__puntuacion')
    ).order_by('-promedio')
    
    # Paginación: 12 películas por página
    paginator = Paginator(peliculas_list, 12)
    page_number = request.GET.get('page')
    peliculas = paginator.get_page(page_number)
    
    # Obtener géneros para el menú
    generos = Genero.objects.all()
    
    context = {
        'genero': genero,
        'peliculas': peliculas,
        'generos': generos,
    }
    return render(request, 'peliculas/por_genero.html', context)


def buscar(request):
    """
    Vista de búsqueda de películas.
    
    Busca películas por título, título original, sinopsis,
    género o director usando el parámetro 'q' en la query string.
    """
    
    # Obtiene y limpia el término de búsqueda
    query = request.GET.get('q', '').strip()
    peliculas = []
    generos = Genero.objects.all()
    
    # Realiza búsqueda solo si hay término ingresado
    if query:
        # Búsqueda en múltiples campos usando Q objects
        peliculas = Pelicula.objects.filter(
            Q(titulo__icontains=query) |
            Q(titulo_original__icontains=query) |
            Q(sinopsis__icontains=query) |
            Q(generos__nombre__icontains=query) |
            Q(director__nombre__icontains=query)
        ).distinct() # Elimina duplicados de relaciones many-to-many
    
    context = {
        'query': query,
        'peliculas': peliculas,
        'generos': generos,
    }
    return render(request, 'peliculas/buscar.html', context)


@login_required
def agregar_calificacion(request, pelicula_id):
    """
    Vista para agregar o actualizar calificación de una película.
    
    Permite calificar películas en escala 1-10. Si el usuario
    ya calificó, actualiza la calificación existente.
    """
    if request.method == 'POST':
        # Obtiene la película o retorna 404
        pelicula = get_object_or_404(Pelicula, pk=pelicula_id)
        # Obtiene puntuación del formulario
        puntuacion = int(request.POST.get('puntuacion', 0))
        
        # Valida que la puntuación esté en el rango permitido
        if 1 <= puntuacion <= 10:
            # Crea nueva calificación o actualiza existente
            calificacion, created = Calificacion.objects.update_or_create(
                pelicula=pelicula,
                usuario=request.user,
                defaults={'puntuacion': puntuacion}
            )
            
            # Mensaje de éxito diferente según si es nueva o actualizada
            if created:
                messages.success(request, '¡Calificación agregada exitosamente!')
            else:
                messages.success(request, '¡Calificación actualizada!')
        else:
            messages.error(request, 'La calificación debe estar entre 1 y 10.')
    
    # Redirige de vuelta a la página de detalle
    return redirect('peliculas:detalle', pelicula_id=pelicula_id)


@login_required
def agregar_resena(request, pelicula_id):
    """
    Vista para agregar o actualizar reseña de una película.
    
    Permite escribir reseñas con título y contenido.
    Un usuario solo puede tener una reseña por película.
    """
    if request.method == 'POST':
        # Obtiene la película o retorna 404
        pelicula = get_object_or_404(Pelicula, pk=pelicula_id)
        # Obtiene datos del formulario
        titulo = request.POST.get('titulo', '')
        contenido = request.POST.get('contenido', '')
        
        # Valida que ambos campos estén completos
        if titulo and contenido:
            resena, created = Resena.objects.update_or_create(
                pelicula=pelicula,
                usuario=request.user,
                defaults={
                    'titulo': titulo,
                    'contenido': contenido
                }
            )
            
            # Mensaje de éxito diferente según si es nueva o actualizada
            if created:
                messages.success(request, '¡Reseña publicada exitosamente!')
            else:
                messages.success(request, '¡Reseña actualizada!')
        else:
            messages.error(request, 'Debes completar todos los campos.')
    # Redirige de vuelta a la página de detalle
    return redirect('peliculas:detalle', pelicula_id=pelicula_id)


def sobre_nosotros(request):
    """
    Vista de la página 'Sobre Nosotros'.
    
    Página estática con información sobre la plataforma.
    """
    generos = Genero.objects.all()
    return render(request, 'peliculas/sobre_nosotros.html', {'generos': generos})


def terminos_condiciones(request):
    """
    Vista para mostrar términos y condiciones.
    
    Muestra el documento legal de términos, condiciones y
    licencia Creative Commons.
    """
    return render(request, 'peliculas/terminos_condiciones.html')


def registro(request):
    """
    Vista de registro de nuevos usuarios.
    
    Maneja el formulario de registro, crea la cuenta,
    autentica automáticamente al usuario y lo redirige.
    Redirige a usuarios ya autenticados al inicio.
    """
    
    # Redirige a inicio si ya está autenticado
    if request.user.is_authenticated:
        return redirect('peliculas:index')
    
    generos = Genero.objects.all()
    
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            # Guarda el nuevo usuario
            user = form.save()
            # Obtiene credenciales para autenticación automática
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f'Bienvenido {username}! Tu cuenta ha sido creada exitosamente.')
            
            if user.is_staff:
                return redirect('/admin/')
            return redirect('peliculas:index')
    else:
        # Formulario vacío para GET
        form = RegistroUsuarioForm()
    
    return render(request, 'peliculas/registro.html', {'form': form, 'generos': generos})


@login_required
def agregar_favoritos(request, pelicula_id):
    """
    Agregar o quitar película de favoritos.
    
    Funciona como toggle: si está en favoritos la quita,
    si no está la agrega.
    """
    pelicula = get_object_or_404(Pelicula, pk=pelicula_id)
    
    # Verifica si la película ya está en favoritos
    if request.user.peliculas_favoritas.filter(id=pelicula_id).exists():
        # Quita de favoritos
        request.user.peliculas_favoritas.remove(pelicula)
        messages.success(request, f'"{pelicula.titulo}" eliminada de tus favoritos.')
    else:
        # Agrega a favoritos
        request.user.peliculas_favoritas.add(pelicula)
        messages.success(request, f'"{pelicula.titulo}" agregada a tus favoritos.')
    
    # Redirige de vuelta a la página de detalle
    return redirect('peliculas:detalle', pelicula_id=pelicula_id)


@login_required
def agregar_ver_despues(request, pelicula_id):
    """
    Agregar o quitar película de la lista 'Ver Después'.
    
    Funciona como toggle: si está en la lista la quita,
    si no está la agrega.
    """
    pelicula = get_object_or_404(Pelicula, pk=pelicula_id)
    
    if request.user.peliculas_ver_despues.filter(id=pelicula_id).exists():
        request.user.peliculas_ver_despues.remove(pelicula)
        messages.success(request, f'"{pelicula.titulo}" eliminada de tu lista.')
    else:
        request.user.peliculas_ver_despues.add(pelicula)
        messages.success(request, f'"{pelicula.titulo}" agregada a Ver Despues.')
    
    return redirect('peliculas:detalle', pelicula_id=pelicula_id)


@login_required
def mi_perfil(request):
    """Vista del perfil del usuario autenticado.
    Muestra favoritos, lista ver después, calificaciones,reseñas y recomendaciones personalizadas."""
    favoritos = request.user.peliculas_favoritas.all()
    ver_despues = request.user.peliculas_ver_despues.all()
    # Obtiene calificaciones y reseñas con optimización de consultas
    mis_calificaciones = Calificacion.objects.filter(usuario=request.user).select_related('pelicula')
    mis_resenas = Resena.objects.filter(usuario=request.user).select_related('pelicula')
    
    # Recomendaciones personalizadas
    # Recomendaciones personalizadas - SOLO AVENTURA
    recomendaciones = obtener_recomendaciones_aventura(request.user)[:12]
    
    generos = Genero.objects.all()
    
    context = {
        'favoritos': favoritos,
        'ver_despues': ver_despues,
        'mis_calificaciones': mis_calificaciones,
        'mis_resenas': mis_resenas,
        'recomendaciones': recomendaciones,
        'generos': generos,
    }
    return render(request, 'peliculas/perfil.html', context)


@login_required
def nueva_pelicula(request):
    """Vista para agregar una nueva pelicula"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para acceder a esta pagina.')
        return redirect('peliculas:index')
    
    generos = Genero.objects.all()
    
    if request.method == 'POST':
        form = PeliculaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nueva pelicula agregada exitosamente!')
            return redirect('peliculas:index')
    else:
        form = PeliculaForm()
    
    return render(request, 'peliculas/nueva_pelicula.html', {'form': form, 'generos': generos})


# ========================================
# VISTAS DE SISTEMA SOCIAL Y MENSAJERIA
# ========================================

@login_required
def lista_conversaciones(request):
    """Lista de conversaciones del usuario"""
    conversaciones = request.user.conversaciones.all().prefetch_related(
        'participantes',
        'mensajes__remitente'  
    ).order_by('-ultima_actividad')
    
    generos = Genero.objects.all()
    
    # Contar mensajes no leídos totales y añadir info del otro usuario
    total_no_leidos = 0
    conversaciones_con_info = []
    
    for conv in conversaciones:
        # Obtener el otro participante
        otro_usuario = conv.participantes.exclude(id=request.user.id).first()
        
        # Contar mensajes no leídos
        mensajes_no_leidos = conv.mensajes_no_leidos(request.user)
        total_no_leidos += mensajes_no_leidos
        
        # Obtener último mensaje
        ultimo_mensaje = conv.ultimo_mensaje()
        
        # Crear objeto con información completa
        conversaciones_con_info.append({
            'conversacion': conv,
            'otro_usuario': otro_usuario,
            'mensajes_no_leidos': mensajes_no_leidos,
            'ultimo_mensaje': ultimo_mensaje,
        })
    
    context = {
        'conversaciones_con_info': conversaciones_con_info,
        'generos': generos,
        'total_no_leidos': total_no_leidos,
    }
    return render(request, 'peliculas/mensajeria/lista_conversaciones.html', context)


@login_required
def conversacion(request, conversacion_id):
    """Vista de una conversacion especifica"""
    conversacion = get_object_or_404(
        Conversacion, 
        pk=conversacion_id, 
        participantes=request.user
    )
    
    # Marcar mensajes como leidos
    mensajes_no_leidos = conversacion.mensajes.filter(
        leido=False
    ).exclude(
        remitente=request.user
    )
    
    for mensaje in mensajes_no_leidos:
        mensaje.marcar_como_leido()
    
    # Obtener todos los mensajes
    mensajes = conversacion.mensajes.select_related('remitente').order_by('fecha_envio')
    
    # Obtener el otro participante
    participantes = conversacion.participantes.exclude(id=request.user.id)
    otro_usuario = participantes.first() if participantes.exists() else None
    
    if request.method == 'POST':
        form = MensajeForm(request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.conversacion = conversacion
            mensaje.remitente = request.user
            mensaje.save()
            
            # Crear notificacion para el otro usuario
            if otro_usuario:
                Notificacion.objects.create(
                    usuario=otro_usuario,
                    tipo='mensaje',
                    titulo='Nuevo mensaje',
                    mensaje=f'{request.user.get_full_name() or request.user.username} te envia un mensaje',
                    url=f'/mensajes/{conversacion.id}/'
                )
            
            messages.success(request, 'Mensaje enviado')
            return redirect('peliculas:conversacion', conversacion_id=conversacion.id)
    else:
        form = MensajeForm()
    
    generos = Genero.objects.all()
    
    context = {
        'conversacion': conversacion,
        'mensajes': mensajes,
        'form': form,
        'otro_usuario': otro_usuario,
        'generos': generos,
    }
    return render(request, 'peliculas/mensajeria/conversacion.html', context)


@login_required
def nueva_conversacion(request, usuario_id):
    """Crear una nueva conversacion con un usuario """
    otro_usuario = get_object_or_404(User, pk=usuario_id)
    
    if otro_usuario == request.user:
        messages.error(request, 'No puedes iniciar una conversacion contigo mismo.')
        return redirect('peliculas:index')
    
    # Verificar si ya existe una conversacion entre estos dos usuarios
    conversacion_existente = Conversacion.objects.filter(
        participantes=request.user
    ).filter(
        participantes=otro_usuario
    ).annotate(
        num_participantes=Count('participantes')
    ).filter(
        num_participantes=2
    ).first()
    
    if conversacion_existente:
        return redirect('peliculas:conversacion', conversacion_id=conversacion_existente.id)
    
    # Crear nueva conversacion
    conversacion = Conversacion.objects.create()
    conversacion.participantes.add(request.user, otro_usuario)
    conversacion.save()
    
    messages.success(request, f'Conversacion iniciada con {otro_usuario.get_full_name() or otro_usuario.username}')
    return redirect('peliculas:conversacion', conversacion_id=conversacion.id)


@login_required
def notificaciones(request):
    """Vista de notificaciones del usuario"""
    notificaciones_list = request.user.notificaciones.order_by('-fecha_creacion')
    
    # Marcar como leidas al visitarlas
    notificaciones_list.filter(leida=False).update(leida=True)
    
    generos = Genero.objects.all()
    
    context = {
        'notificaciones': notificaciones_list,
        'generos': generos,
    }
    return render(request, 'peliculas/notificaciones.html', context)


@login_required
def notificaciones_json(request):
    """API JSON para notificaciones no leidas"""
    notificaciones = request.user.notificaciones.filter(
        leida=False
    ).order_by('-fecha_creacion')[:10]
    
    data = {
        'count': notificaciones.count(),
        'notificaciones': [
            {
                'id': n.id,
                'tipo': n.tipo,
                'titulo': n.titulo,
                'mensaje': n.mensaje,
                'url': n.url,
                'fecha': n.fecha_creacion.strftime('%Y-%m-%d %H:%M')
            }
            for n in notificaciones
        ]
    }
    return JsonResponse(data)

# ========================================
# VISTAS DE SOCIAL HUB Y PERFILES
# ========================================

@login_required
def social_hub(request):
    """Vista del Social Hub - Explorar usuarios"""
    query = request.GET.get('q', '').strip()
    
    # Excluir al usuario actual de los resultados
    usuarios_list = User.objects.exclude(id=request.user.id).annotate(
        total_calificaciones=Count('calificaciones'),
        total_resenas=Count('resenas'),
        peliculas_favoritas_count=Count('peliculas_favoritas')
    )
    
    # Filtrar por búsqueda si existe
    if query:
        usuarios_list = usuarios_list.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    
    # Ordenar por actividad (más calificaciones y reseñas)
    usuarios_list = usuarios_list.order_by('-total_calificaciones', '-total_resenas')
    
    # Paginación
    paginator = Paginator(usuarios_list, 12)
    page_number = request.GET.get('page')
    usuarios = paginator.get_page(page_number)
    
    generos = Genero.objects.all()
    
    context = {
        'usuarios': usuarios,
        'query': query,
        'total_usuarios': User.objects.count() - 1,  # -1 para excluir al usuario actual
        'generos': generos,
    }
    return render(request, 'peliculas/social_hub.html', context)


@login_required
def perfil_usuario(request, usuario_id):
    """Vista del perfil público de un usuario"""
    usuario_perfil = get_object_or_404(User, pk=usuario_id)
    
    # No permitir que vea su propio perfil aquí (redirigir a mi_perfil)
    if usuario_perfil == request.user:
        return redirect('peliculas:perfil')
    
    # Obtener datos del usuario
    favoritos = usuario_perfil.peliculas_favoritas.all()[:12]
    calificaciones = Calificacion.objects.filter(usuario=usuario_perfil).select_related('pelicula').order_by('-fecha')[:10]
    resenas = Resena.objects.filter(usuario=usuario_perfil).select_related('pelicula').order_by('-fecha')[:5]
    
    # Verificar si ya existe una conversación
    conversacion_existente = Conversacion.objects.filter(
        participantes=request.user
    ).filter(
        participantes=usuario_perfil
    ).annotate(
        num_participantes=Count('participantes')
    ).filter(
        num_participantes=2
    ).first()
    
    generos = Genero.objects.all()
    
    context = {
        'usuario_perfil': usuario_perfil,
        'favoritos': favoritos,
        'calificaciones': calificaciones,
        'resenas': resenas,
        'conversacion_existente': conversacion_existente,
        'generos': generos,
    }
    return render(request, 'peliculas/perfil_usuario.html', context)



@login_required
def mensajes_no_leidos_json(request):
    """API JSON para mensajes no leídos por conversación"""
    conversaciones = request.user.conversaciones.all().prefetch_related(
        'participantes',
        'mensajes__remitente'
    ).order_by('-ultima_actividad')
    
    data_conversaciones = []
    total_no_leidos = 0
    
    for conv in conversaciones:
        mensajes_no_leidos = conv.mensajes_no_leidos(request.user)
        total_no_leidos += mensajes_no_leidos
        
        if mensajes_no_leidos > 0:
            ultimo_mensaje = conv.ultimo_mensaje()
            otro_usuario = conv.participantes.exclude(id=request.user.id).first()
            
            data_conversaciones.append({
                'id': conv.id,
                'mensajes_no_leidos': mensajes_no_leidos,
                'otro_usuario': otro_usuario.get_full_name() or otro_usuario.username if otro_usuario else 'Usuario',
                'ultimo_mensaje_id': ultimo_mensaje.id if ultimo_mensaje else None,
                'ultimo_mensaje_preview': ultimo_mensaje.contenido[:50] if ultimo_mensaje else '',
            })
    
    return JsonResponse({
        'total_no_leidos': total_no_leidos,
        'conversaciones': data_conversaciones
    })


# ========================================
# ALGORITMO DE RECOMENDACIONES
# ========================================

def obtener_recomendaciones_aventura(usuario, limite=12):
    """Algoritmo de recomendacion personalizado - SOLO PELICULAS DE AVENTURA"""
    
    # Obtener género aventura
    genero_aventura = Genero.objects.filter(nombre__iexact='aventura').first()
    if not genero_aventura:
        return Pelicula.objects.none()
    
    # Obtener películas ya vistas
    peliculas_vistas = set()
    peliculas_vistas.update(usuario.peliculas_favoritas.values_list('id', flat=True))
    peliculas_vistas.update(usuario.calificaciones.values_list('pelicula_id', flat=True))
    peliculas_vistas.update(usuario.historial.values_list('pelicula_id', flat=True))
    
    # Obtener calificaciones altas del usuario en películas de aventura
    calificaciones_altas = usuario.calificaciones.filter(
        puntuacion__gte=7,
        pelicula__generos=genero_aventura
    )
    
    # Películas de aventura recomendadas por calificación
    recomendaciones_genero = Pelicula.objects.filter(
        generos=genero_aventura
    ).exclude(
        id__in=peliculas_vistas
    ).annotate(
        promedio=Avg('calificaciones__puntuacion'),
        total_calificaciones=Count('calificaciones')
    ).filter(
        total_calificaciones__gte=1
    ).order_by('-promedio', '-total_calificaciones')[:limite//2]
    
    # Filtrado colaborativo - solo aventura
    usuarios_similares = User.objects.filter(
        calificaciones__pelicula__in=usuario.peliculas_favoritas.filter(generos=genero_aventura)
    ).exclude(
        id=usuario.id
    ).annotate(
        coincidencias=Count('id')
    ).order_by('-coincidencias')[:5]
    
    recomendaciones_colaborativas = Pelicula.objects.filter(
        generos=genero_aventura,
        calificaciones__usuario__in=usuarios_similares,
        calificaciones__puntuacion__gte=7
    ).exclude(
        id__in=peliculas_vistas
    ).annotate(
        promedio=Avg('calificaciones__puntuacion')
    ).order_by('-promedio')[:limite//2]
    
    # Combinar recomendaciones
    recomendaciones = list(recomendaciones_genero) + list(recomendaciones_colaborativas)
    
    # Eliminar duplicados
    recomendaciones_unicas = []
    ids_vistos = set()
    for pelicula in recomendaciones:
        if pelicula.id not in ids_vistos:
            recomendaciones_unicas.append(pelicula)
            ids_vistos.add(pelicula.id)
    
    return recomendaciones_unicas[:limite]


@login_required
def recomendaciones_view(request):
    """Vista dedicada a recomendaciones personalizadas - SOLO AVENTURA"""
    recomendaciones = obtener_recomendaciones_aventura(request.user, limite=24)
    generos = Genero.objects.all()
    
    context = {
        'recomendaciones': recomendaciones,
        'generos': generos,
    }
    return render(request, 'peliculas/recomendaciones.html', context)


# ========================================
# WATCH PARTIES
# ========================================

@login_required
def lista_watch_parties(request):
    """Lista de watch parties disponibles"""
    mis_parties = WatchParty.objects.filter(
        Q(anfitrion=request.user) | Q(participantes=request.user)
    ).distinct().order_by('-fecha_programada')
    
    parties_publicas = WatchParty.objects.filter(
        publico=True,
        estado='esperando',
        fecha_programada__gte=timezone.now()
    ).exclude(
        Q(anfitrion=request.user) | Q(participantes=request.user)
    ).order_by('fecha_programada')
    
    generos = Genero.objects.all()
    
    context = {
        'mis_parties': mis_parties,
        'parties_publicas': parties_publicas,
        'generos': generos,
    }
    return render(request, 'peliculas/watch_parties/lista.html', context)


@login_required
def crear_watch_party(request, pelicula_id):
    """Crear un nuevo watch party"""
    pelicula = get_object_or_404(Pelicula, pk=pelicula_id)
    
    if request.method == 'POST':
        form = WatchPartyForm(request.POST)
        if form.is_valid():
            watch_party = form.save(commit=False)
            watch_party.pelicula = pelicula
            watch_party.anfitrion = request.user
            watch_party.codigo_invitacion = ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )
            watch_party.save()
            watch_party.participantes.add(request.user)
            
            messages.success(request, f'Watch Party "{watch_party.nombre}" creado exitosamente!')
            return redirect('peliculas:detalle_watch_party', party_id=watch_party.id)
    else:
        form = WatchPartyForm(initial={
            'fecha_programada': timezone.now() + timezone.timedelta(hours=1)
        })
    
    generos = Genero.objects.all()
    
    context = {
        'form': form,
        'pelicula': pelicula,
        'generos': generos,
    }
    return render(request, 'peliculas/watch_parties/crear.html', context)


@login_required
def detalle_watch_party(request, party_id):
    """Vista detallada de un watch party"""
    watch_party = get_object_or_404(WatchParty, pk=party_id)
    
    es_participante = request.user in watch_party.participantes.all()
    es_anfitrion = request.user == watch_party.anfitrion
    mensajes_chat = watch_party.mensajes_chat.select_related('usuario').order_by('fecha_envio')
    
    generos = Genero.objects.all()
    
    context = {
        'watch_party': watch_party,
        'es_participante': es_participante,
        'es_anfitrion': es_anfitrion,
        'mensajes_chat': mensajes_chat,
        'generos': generos,
    }
    return render(request, 'peliculas/watch_parties/detalle.html', context)


@login_required
def unirse_watch_party(request, party_id):
    """Unirse a un watch party"""
    watch_party = get_object_or_404(WatchParty, pk=party_id)
    
    if not watch_party.puede_unirse():
        messages.error(request, 'Este Watch Party esta lleno.')
        return redirect('peliculas:detalle_watch_party', party_id=party_id)
    
    if request.user not in watch_party.participantes.all():
        watch_party.participantes.add(request.user)
        messages.success(request, f'Te has unido a "{watch_party.nombre}"!')
        
        Notificacion.objects.create(
            usuario=watch_party.anfitrion,
            tipo='watch_party',
            titulo='Nuevo participante',
            mensaje=f'{request.user.get_full_name() or request.user.username} se unio a tu Watch Party',
            url=f'/watch-parties/{watch_party.id}/'
        )
    
    return redirect('peliculas:detalle_watch_party', party_id=party_id)


@login_required
def salir_watch_party(request, party_id):
    """Salir de un watch party"""
    watch_party = get_object_or_404(WatchParty, pk=party_id)
    
    if request.user in watch_party.participantes.all():
        watch_party.participantes.remove(request.user)
        messages.success(request, f'Has salido de "{watch_party.nombre}".')
    
    return redirect('peliculas:lista_watch_parties')


@login_required
def enviar_mensaje_watch_party(request, party_id):
    """Enviar mensaje en el chat del watch party"""
    if request.method == 'POST':
        watch_party = get_object_or_404(WatchParty, pk=party_id)
        
        if request.user not in watch_party.participantes.all():
            return JsonResponse({'error': 'No eres participante'}, status=403)
        
        contenido = request.POST.get('contenido', '').strip()
        if contenido:
            mensaje = MensajeWatchParty.objects.create(
                watch_party=watch_party,
                usuario=request.user,
                contenido=contenido
            )
            
            return JsonResponse({
                'success': True,
                'mensaje': {
                    'id': mensaje.id,
                    'usuario': mensaje.usuario.get_full_name() or mensaje.usuario.username,
                    'contenido': mensaje.contenido,
                    'fecha': mensaje.fecha_envio.strftime('%H:%M')
                }
            })
        
        return JsonResponse({'error': 'Mensaje vacio'}, status=400)
    
    return JsonResponse({'error': 'Metodo no permitido'}, status=405)

from .tmdb_service import TMDBService, GENRE_MAPPING

@login_required
def buscar_tmdb(request):
    """Vista para buscar películas en TMDB"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('peliculas:index')
    
    tmdb = TMDBService()
    resultados = []
    query = request.GET.get('q', '').strip()
    
    if query:
        data = tmdb.buscar_peliculas(query)
        if data and 'results' in data:
            resultados = data['results'][:20]  # Limitar a 20 resultados
    
    generos = Genero.objects.all()
    
    context = {
        'resultados': resultados,
        'query': query,
        'generos': generos,
    }
    return render(request, 'peliculas/tmdb_buscar.html', context)


@login_required
def importar_pelicula_tmdb(request, tmdb_id):
    """Importa una película desde TMDB a la base de datos local"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('peliculas:index')
    
    tmdb = TMDBService()
    
    # Obtener datos de TMDB
    movie_data = tmdb.obtener_detalles_pelicula(tmdb_id)
    
    if not movie_data:
        messages.error(request, 'No se pudo obtener la información de la película.')
        return redirect('peliculas:buscar_tmdb')
    
    # Formatear datos
    datos_formateados = tmdb.formatear_pelicula_para_db(movie_data)
    
    if not datos_formateados:
        messages.error(request, 'Error al procesar los datos de la película.')
        return redirect('peliculas:buscar_tmdb')
    
    try:
        # Verificar si ya existe
        if Pelicula.objects.filter(titulo=datos_formateados['titulo'], año=datos_formateados['año']).exists():
            messages.warning(request, f'La película "{datos_formateados["titulo"]}" ya existe en la base de datos.')
            return redirect('peliculas:buscar_tmdb')
        
        # Crear o obtener director
        director = None
        if datos_formateados['director_nombre']:
            director, _ = Director.objects.get_or_create(
                nombre=datos_formateados['director_nombre'],
                defaults={'nacionalidad': datos_formateados['pais']}
            )
        
        # Crear película
        pelicula = Pelicula.objects.create(
            titulo=datos_formateados['titulo'],
            titulo_original=datos_formateados['titulo_original'],
            sinopsis=datos_formateados['sinopsis'],
            año=datos_formateados['año'],
            duracion=datos_formateados['duracion'],
            director=director,
            pais=datos_formateados['pais'],
            idioma=datos_formateados['idioma'],
            poster=datos_formateados['poster'],
            trailer=datos_formateados['trailer'],
            fecha_estreno=datos_formateados['fecha_estreno'],
            presupuesto=datos_formateados['presupuesto'],
            recaudacion=datos_formateados['recaudacion'],
            clasificacion='PG-13'  # Valor por defecto
        )
        
        # Asignar géneros
        for genre_name in datos_formateados['generos_nombres']:
            genero, _ = Genero.objects.get_or_create(nombre=genre_name)
            pelicula.generos.add(genero)
        
        # Crear actores
        for actor_nombre in datos_formateados['actores_nombres']:
            actor, _ = Actor.objects.get_or_create(
                nombre=actor_nombre,
                defaults={'nacionalidad': datos_formateados['pais']}
            )
            pelicula.actores.add(actor)
        
        pelicula.save()
        
        messages.success(request, f'¡Película "{pelicula.titulo}" importada exitosamente!')
        return redirect('peliculas:detalle', pelicula_id=pelicula.id)
        
    except Exception as e:
        messages.error(request, f'Error al importar la película: {str(e)}')
        return redirect('peliculas:buscar_tmdb')