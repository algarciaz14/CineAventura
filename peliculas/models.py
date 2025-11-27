from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q


class Genero(models.Model):
    """Modelo para los géneros cinematográficos"""
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Género"
        verbose_name_plural = "Géneros"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Director(models.Model):
    """Modelo para directores de películas"""
    nombre = models.CharField(max_length=200)
    biografia = models.TextField(blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    nacionalidad = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = "Director"
        verbose_name_plural = "Directores"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Actor(models.Model):
    """Modelo para actores"""
    nombre = models.CharField(max_length=200)
    biografia = models.TextField(blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    nacionalidad = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = "Actor"
        verbose_name_plural = "Actores"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Pelicula(models.Model):
    """Modelo principal para películas"""
    titulo = models.CharField(max_length=300)
    titulo_original = models.CharField(max_length=300, blank=True)
    sinopsis = models.TextField()
    año = models.IntegerField(
        validators=[MinValueValidator(1888), MaxValueValidator(2030)]
    )
    duracion = models.IntegerField(help_text="Duración en minutos")
    generos = models.ManyToManyField(Genero, related_name='peliculas')
    director = models.ForeignKey(
        Director, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='peliculas'
    )
    actores = models.ManyToManyField(Actor, related_name='peliculas', blank=True)
    pais = models.CharField(max_length=100)
    idioma = models.CharField(max_length=100)
    poster = models.URLField(blank=True, help_text="URL del poster de la película")
    trailer = models.URLField(blank=True, help_text="URL del trailer (YouTube)")
    fecha_estreno = models.DateField()
    presupuesto = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Presupuesto en USD"
    )
    recaudacion = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Recaudación mundial en USD"
    )
    clasificacion = models.CharField(
        max_length=10,
        choices=[
            ('G', 'G - Público General'),
            ('PG', 'PG - Se sugiere orientación parental'),
            ('PG-13', 'PG-13 - Mayores de 13 años'),
            ('R', 'R - Restringida'),
            ('NC-17', 'NC-17 - Solo adultos'),
        ],
        default='PG-13'
    )
    fecha_agregada = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    actualizada = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        verbose_name = "Película"
        verbose_name_plural = "Películas"
        ordering = ['-año', 'titulo']
    
    def __str__(self):
        return f"{self.titulo} ({self.año})"
    
    def calificacion_promedio(self):
        """Calcula la calificación promedio de la película"""
        calificaciones = self.calificaciones.all()
        if calificaciones:
            return round(sum(c.puntuacion for c in calificaciones) / len(calificaciones), 1)
        return 0
    
    def total_resenas(self):
        """Retorna el total de reseñas"""
        return self.resenas.count()

class Calificacion(models.Model):
    """Modelo para calificaciones de usuarios"""
    pelicula = models.ForeignKey(
        Pelicula, 
        on_delete=models.CASCADE, 
        related_name='calificaciones'
    )
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='calificaciones'
    )
    puntuacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Calificación"
        verbose_name_plural = "Calificaciones"
        unique_together = ['pelicula', 'usuario']
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.pelicula.titulo}: {self.puntuacion}/10"

class Resena(models.Model):
    """Modelo para reseñas de usuarios"""
    pelicula = models.ForeignKey(
        Pelicula, 
        on_delete=models.CASCADE, 
        related_name='resenas'
    )
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='resenas'
    )
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)
    util_count = models.IntegerField(default=0, help_text="Votos de utilidad")
    
    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        unique_together = ['pelicula', 'usuario']
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.pelicula.titulo}"

class ListaPersonalizada(models.Model):
    """Modelo para listas personalizadas de usuarios"""
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='listas'
    )
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    peliculas = models.ManyToManyField(Pelicula, related_name='en_listas', blank=True)
    publica = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Lista Personalizada"
        verbose_name_plural = "Listas Personalizadas"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.nombre} - {self.usuario.username}"


# ========================
# NUEVOS MODELOS 
# ========================

class PerfilUsuario(models.Model):
    """Extensión del modelo User para términos y condiciones"""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    aceptado_terminos = models.BooleanField(default=False)
    fecha_aceptacion_terminos = models.DateTimeField(null=True, blank=True)
    version_terminos = models.CharField(max_length=10, default='1.0')
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"


class Conversacion(models.Model):
    """Modelo para conversaciones entre usuarios"""
    participantes = models.ManyToManyField(User, related_name='conversaciones')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_actividad = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Conversación"
        verbose_name_plural = "Conversaciones"
        ordering = ['-ultima_actividad']
    
    def __str__(self):
        usuarios = ", ".join([u.username for u in self.participantes.all()[:2]])
        return f"Conversación: {usuarios}"
    
    def ultimo_mensaje(self):
        """Obtiene el último mensaje de la conversación"""
        return self.mensajes.order_by('-fecha_envio').first()
    
    def mensajes_no_leidos(self, usuario):
        """Cuenta mensajes no leídos para un usuario específico"""
        return self.mensajes.filter(
            leido=False
        ).exclude(
        remitente=usuario
        ).count()


class Mensaje(models.Model):
    """Modelo para mensajes individuales"""
    conversacion = models.ForeignKey(
        Conversacion, 
        on_delete=models.CASCADE, 
        related_name='mensajes'
    )
    remitente = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='mensajes_enviados'
    )
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"
        ordering = ['fecha_envio']
    
    def __str__(self):
        return f"{self.remitente.username}: {self.contenido[:30]}..."
    
    def marcar_como_leido(self):
        """Marca el mensaje como leído"""
        if not self.leido:
            self.leido = True
            self.fecha_lectura = timezone.now()
            self.save()


class Notificacion(models.Model):
    """Modelo para notificaciones de usuarios"""
    TIPOS = [
        ('mensaje', 'Nuevo Mensaje'),
        ('watch_party', 'Invitación a Watch Party'),
        ('resena', 'Nueva Reseña'),
        ('sistema', 'Notificación del Sistema'),
    ]
    
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notificaciones'
    )
    tipo = models.CharField(max_length=20, choices=TIPOS)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    url = models.CharField(max_length=500, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.tipo} para {self.usuario.username}: {self.titulo}"


class HistorialVisualizacion(models.Model):
    """Modelo para tracking de visualizaciones y recomendaciones"""
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='historial'
    )
    pelicula = models.ForeignKey(
        Pelicula, 
        on_delete=models.CASCADE, 
        related_name='visualizaciones'
    )
    fecha_visualizacion = models.DateTimeField(auto_now_add=True)
    duracion_vista = models.IntegerField(
        default=0, 
        help_text="Minutos vistos"
    )
    completada = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Historial de Visualización"
        verbose_name_plural = "Historiales de Visualización"
        ordering = ['-fecha_visualizacion']
        unique_together = ['usuario', 'pelicula', 'fecha_visualizacion']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.pelicula.titulo}"


class WatchParty(models.Model):
    """Modelo para Watch Parties (ver películas en grupo)"""
    ESTADOS = [
        ('esperando', 'Esperando'),
        ('en_curso', 'En Curso'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]
    
    pelicula = models.ForeignKey(
        Pelicula, 
        on_delete=models.CASCADE, 
        related_name='watch_parties'
    )
    anfitrion = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='watch_parties_creadas'
    )
    participantes = models.ManyToManyField(
        User, 
        related_name='watch_parties_participando', 
        blank=True
    )
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha_programada = models.DateTimeField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='esperando')
    
    # Control de reproducción sincronizada
    tiempo_actual = models.IntegerField(
        default=0, 
        help_text="Segundo actual del video"
    )
    esta_reproduciendo = models.BooleanField(default=False)
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    # Configuración
    publico = models.BooleanField(
        default=False, 
        help_text="Si es público, cualquiera puede unirse"
    )
    max_participantes = models.IntegerField(default=10)
    codigo_invitacion = models.CharField(max_length=20, unique=True, blank=True)
    
    class Meta:
        verbose_name = "Watch Party"
        verbose_name_plural = "Watch Parties"
        ordering = ['-fecha_programada']
    
    def __str__(self):
        return f"{self.nombre} - {self.pelicula.titulo}"
    
    def puede_unirse(self):
        """Verifica si hay espacio para más participantes"""
        return self.participantes.count() < self.max_participantes
    
    def total_participantes(self):
        """Retorna el total de participantes"""
        return self.participantes.count()
    
    def iniciar(self):
        """Inicia el watch party"""
        self.estado = 'en_curso'
        self.save()
    
    def finalizar(self):
        """Finaliza el watch party"""
        self.estado = 'finalizada'
        self.save()


class MensajeWatchParty(models.Model):
    """Mensajes del chat durante un Watch Party"""
    watch_party = models.ForeignKey(
        WatchParty, 
        on_delete=models.CASCADE, 
        related_name='mensajes_chat'
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Mensaje de Watch Party"
        verbose_name_plural = "Mensajes de Watch Party"
        ordering = ['fecha_envio']
    
    def __str__(self):
        return f"{self.usuario.username} en {self.watch_party.nombre}: {self.contenido[:30]}"


# Extensiones al modelo User
User.add_to_class(
    'peliculas_favoritas',
    models.ManyToManyField(
        Pelicula,  
        related_name='usuarios_favorito',
        blank=True
    )
)

User.add_to_class(
    'peliculas_ver_despues',
    models.ManyToManyField(
        Pelicula,  
        related_name='usuarios_ver_despues',
        blank=True
    )
)