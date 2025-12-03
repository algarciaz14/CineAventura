from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q


class Genero(models.Model):
    """
    Modelo para los géneros cinematográficos.
    
    Representa categorías de películas como Acción, Drama, Comedia, etc.
    Permite clasificar y filtrar películas por género.
    """
    # Nombre único del género (ej: "Acción", "Drama")
    nombre = models.CharField(max_length=50, unique=True)
    # Descripción opcional del género
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Género"
        verbose_name_plural = "Géneros"
        # Ordena géneros alfabéticamente por nombre
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Director(models.Model):
    """
    Modelo para directores de películas.
    
    Almacena información biográfica y profesional de directores de cine.
    """
    # Nombre completo del director
    nombre = models.CharField(max_length=200)
    # Biografía opcional del director
    biografia = models.TextField(blank=True)
    # Fecha de nacimiento (opcional)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    # País de origen del director
    nacionalidad = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = "Director"
        verbose_name_plural = "Directores"
        # Ordena directores alfabéticamente por nombre
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Actor(models.Model):
    """
    Modelo para actores.
    
    Almacena información biográfica de actores que participan en películas.
    """
    # Nombre completo del actor
    nombre = models.CharField(max_length=200)
    # Biografía opcional del actor
    biografia = models.TextField(blank=True)
    # Fecha de nacimiento (opcional)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    # País de origen del actor
    nacionalidad = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = "Actor"
        verbose_name_plural = "Actores"
        # Ordena actores alfabéticamente por nombre
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Pelicula(models.Model):
    """
    Modelo principal para películas.
    
    Contiene toda la información relevante de una película incluyendo
    detalles técnicos, artísticos, financieros y multimedia.
    """
    # Título de la película (puede ser traducido)
    titulo = models.CharField(max_length=300)
    # Título original en idioma nativo (opcional)
    titulo_original = models.CharField(max_length=300, blank=True)
    # Sinopsis o descripción de la trama
    sinopsis = models.TextField()
    # Año de estreno (validado entre 1888 y 2030)
    año = models.IntegerField(
        validators=[MinValueValidator(1888), MaxValueValidator(2030)]
    )
    # Duración de la película en minutos
    duracion = models.IntegerField(help_text="Duración en minutos")
    # Relación many-to-many con géneros (una película puede tener varios géneros)
    generos = models.ManyToManyField(Genero, related_name='peliculas')
    # Relación con director (puede ser nulo si se elimina el director)
    director = models.ForeignKey(
        Director, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='peliculas'
    )
    # Relación many-to-many con actores (reparto de la película)
    actores = models.ManyToManyField(Actor, related_name='peliculas', blank=True)
    # País de producción
    pais = models.CharField(max_length=100)
    # Idioma original de la película
    idioma = models.CharField(max_length=100)
    # URL del póster de la película
    poster = models.URLField(blank=True, help_text="URL del poster de la película")
    # URL del trailer (generalmente de YouTube)
    trailer = models.URLField(blank=True, help_text="URL del trailer (YouTube)")
    # Fecha exacta de estreno
    fecha_estreno = models.DateField()
    # Presupuesto de producción en dólares estadounidenses
    presupuesto = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Presupuesto en USD"
    )
    # Recaudación total mundial en dólares
    recaudacion = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Recaudación mundial en USD"
    )
    # Clasificación por edad según sistema estadounidense
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
    # Fecha en que la película fue agregada al sistema
    fecha_agregada = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    # Fecha de última actualización de la información
    actualizada = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        verbose_name = "Película"
        verbose_name_plural = "Películas"
        # Ordena por año descendente, luego por título
        ordering = ['-año', 'titulo']
    
    def __str__(self):
        return f"{self.titulo} ({self.año})"
    
    def calificacion_promedio(self):
        """
        Calcula la calificación promedio de la película.
        
        Returns:
            float: Promedio de calificaciones redondeado a 1 decimal, 0 si no hay calificaciones
        """
        calificaciones = self.calificaciones.all()
        if calificaciones:
            return round(sum(c.puntuacion for c in calificaciones) / len(calificaciones), 1)
        return 0
    
    def total_resenas(self):
        """
        Retorna el total de reseñas escritas para esta película.
        
        Returns:
            int: Número total de reseñas
        """
        return self.resenas.count()


class Calificacion(models.Model):
    """
    Modelo para calificaciones numéricas de usuarios.
    
    Permite a los usuarios calificar películas en una escala del 1 al 10.
    Un usuario solo puede calificar una película una vez.
    """
    # Película que está siendo calificada
    pelicula = models.ForeignKey(
        Pelicula, 
        on_delete=models.CASCADE, 
        related_name='calificaciones'
    )
    # Usuario que realiza la calificación
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='calificaciones'
    )
    # Puntuación del 1 al 10
    puntuacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    # Fecha de creación de la calificación
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Calificación"
        verbose_name_plural = "Calificaciones"
        # Asegura que un usuario solo pueda calificar una película una vez
        unique_together = ['pelicula', 'usuario']
        # Ordena por fecha descendente (más recientes primero)
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.pelicula.titulo}: {self.puntuacion}/10"


class Resena(models.Model):
    """
    Modelo para reseñas escritas de usuarios.
    
    Permite a los usuarios escribir opiniones detalladas sobre películas.
    Incluye título, contenido y sistema de votos de utilidad.
    """
    # Película que está siendo reseñada
    pelicula = models.ForeignKey(
        Pelicula, 
        on_delete=models.CASCADE, 
        related_name='resenas'
    )
    # Usuario que escribe la reseña
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='resenas'
    )
    # Título de la reseña
    titulo = models.CharField(max_length=200)
    # Contenido completo de la reseña
    contenido = models.TextField()
    # Fecha de creación de la reseña
    fecha = models.DateTimeField(auto_now_add=True)
    # Fecha de última actualización
    actualizada = models.DateTimeField(auto_now=True)
    # Contador de votos de utilidad de otros usuarios
    util_count = models.IntegerField(default=0, help_text="Votos de utilidad")
    
    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        # Un usuario solo puede escribir una reseña por película
        unique_together = ['pelicula', 'usuario']
        # Ordena por fecha descendente (más recientes primero)
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.pelicula.titulo}"


class ListaPersonalizada(models.Model):
    """
    Modelo para listas personalizadas de películas.
    
    Permite a los usuarios crear colecciones temáticas de películas
    (ej: "Mis comedias favoritas", "Películas para ver en Halloween").
    """
    # Usuario dueño de la lista
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='listas'
    )
    # Nombre de la lista
    nombre = models.CharField(max_length=200)
    # Descripción opcional de la lista
    descripcion = models.TextField(blank=True)
    # Películas incluidas en la lista (many-to-many)
    peliculas = models.ManyToManyField(Pelicula, related_name='en_listas', blank=True)
    # Visibilidad de la lista (pública o privada)
    publica = models.BooleanField(default=False)
    # Fecha de creación de la lista
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Lista Personalizada"
        verbose_name_plural = "Listas Personalizadas"
        # Ordena por fecha de creación descendente (más recientes primero)
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.nombre} - {self.usuario.username}"


# ========================
# NUEVOS MODELOS 
# ========================

class PerfilUsuario(models.Model):
    """
    Extensión del modelo User para términos y condiciones.
    
    Almacena información legal relacionada con la aceptación de términos
    y condiciones, incluyendo fecha y versión aceptada.
    """
    # Relación uno a uno con el modelo User de Django
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    # Indica si el usuario aceptó los términos y condiciones
    aceptado_terminos = models.BooleanField(default=False)
    # Fecha en que aceptó los términos
    fecha_aceptacion_terminos = models.DateTimeField(null=True, blank=True)
    # Versión de los términos que aceptó
    version_terminos = models.CharField(max_length=10, default='1.0')
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"


class Conversacion(models.Model):
    """
    Modelo para conversaciones entre usuarios.
    
    Representa una conversación privada entre dos o más usuarios,
    conteniendo todos los mensajes intercambiados.
    """
    # Usuarios que participan en la conversación (many-to-many)
    participantes = models.ManyToManyField(User, related_name='conversaciones')
    # Fecha de creación de la conversación
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    # Última vez que hubo actividad (se actualiza automáticamente)
    ultima_actividad = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Conversación"
        verbose_name_plural = "Conversaciones"
        # Ordena por última actividad descendente (más recientes primero)
        ordering = ['-ultima_actividad']
    
    def __str__(self):
        # Muestra los primeros 2 participantes
        usuarios = ", ".join([u.username for u in self.participantes.all()[:2]])
        return f"Conversación: {usuarios}"
    
    def ultimo_mensaje(self):
        """
        Obtiene el último mensaje enviado en la conversación.
        
        Returns:
            Mensaje: Instancia del último mensaje o None si no hay mensajes
        """
        return self.mensajes.order_by('-fecha_envio').first()
    
    def mensajes_no_leidos(self, usuario):
        """
        Cuenta los mensajes no leídos para un usuario específico.
        
        Args:
            usuario (User): Usuario para el cual contar mensajes no leídos
            
        Returns:
            int: Número de mensajes no leídos
        """
        return self.mensajes.filter(
            leido=False
        ).exclude(
            remitente=usuario
        ).count()


class Mensaje(models.Model):
    """
    Modelo para mensajes individuales dentro de una conversación.
    
    Representa un mensaje enviado por un usuario en una conversación,
    incluyendo estado de lectura y timestamp.
    """
    # Conversación a la que pertenece el mensaje
    conversacion = models.ForeignKey(
        Conversacion, 
        on_delete=models.CASCADE, 
        related_name='mensajes'
    )
    # Usuario que envía el mensaje
    remitente = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='mensajes_enviados'
    )
    # Contenido del mensaje
    contenido = models.TextField()
    # Fecha y hora de envío
    fecha_envio = models.DateTimeField(auto_now_add=True)
    # Indica si el mensaje ha sido leído
    leido = models.BooleanField(default=False)
    # Fecha y hora en que fue leído (opcional)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"
        # Ordena por fecha de envío ascendente (cronológico)
        ordering = ['fecha_envio']
    
    def __str__(self):
        # Muestra remitente y primeros 30 caracteres del contenido
        return f"{self.remitente.username}: {self.contenido[:30]}..."
    
    def marcar_como_leido(self):
        """
        Marca el mensaje como leído y registra la fecha de lectura.
        
        Solo marca el mensaje si no estaba previamente leído.
        """
        if not self.leido:
            self.leido = True
            self.fecha_lectura = timezone.now()
            self.save()


class Notificacion(models.Model):
    """
    Modelo para notificaciones de usuarios.
    
    Sistema de notificaciones para alertar a usuarios sobre eventos
    relevantes como mensajes, invitaciones, etc.
    """
    # Tipos de notificaciones disponibles
    TIPOS = [
        ('mensaje', 'Nuevo Mensaje'),
        ('watch_party', 'Invitación a Watch Party'),
        ('resena', 'Nueva Reseña'),
        ('sistema', 'Notificación del Sistema'),
    ]
    
    # Usuario que recibe la notificación
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notificaciones'
    )
    # Tipo de notificación
    tipo = models.CharField(max_length=20, choices=TIPOS)
    # Título de la notificación
    titulo = models.CharField(max_length=200)
    # Mensaje o descripción de la notificación
    mensaje = models.TextField()
    # Indica si la notificación ha sido leída
    leida = models.BooleanField(default=False)
    # URL a la que redirige la notificación (opcional)
    url = models.CharField(max_length=500, blank=True)
    # Fecha de creación de la notificación
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        # Ordena por fecha descendente (más recientes primero)
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.tipo} para {self.usuario.username}: {self.titulo}"


class HistorialVisualizacion(models.Model):
    """
    Modelo para tracking de visualizaciones de películas.
    
    Registra el historial de películas vistas por usuarios,
    útil para generar recomendaciones personalizadas.
    """
    # Usuario que visualiza la película
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='historial'
    )
    # Película visualizada
    pelicula = models.ForeignKey(
        Pelicula, 
        on_delete=models.CASCADE, 
        related_name='visualizaciones'
    )
    # Fecha y hora de la visualización
    fecha_visualizacion = models.DateTimeField(auto_now_add=True)
    # Cantidad de minutos vistos
    duracion_vista = models.IntegerField(
        default=0, 
        help_text="Minutos vistos"
    )
    # Indica si la película fue vista completamente
    completada = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Historial de Visualización"
        verbose_name_plural = "Historiales de Visualización"
        # Ordena por fecha descendente (más recientes primero)
        ordering = ['-fecha_visualizacion']
        # Permite múltiples registros de la misma película en diferentes fechas
        unique_together = ['usuario', 'pelicula', 'fecha_visualizacion']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.pelicula.titulo}"


class WatchParty(models.Model):
    """
    Modelo para Watch Parties (sesiones grupales de visualización).
    
    Permite a usuarios crear eventos para ver películas sincronizadamente
    con otros usuarios en tiempo real, incluyendo chat integrado.
    """
    # Estados posibles del watch party
    ESTADOS = [
        ('esperando', 'Esperando'),
        ('en_curso', 'En Curso'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]
    
    # Película que se verá en el watch party
    pelicula = models.ForeignKey(
        Pelicula, 
        on_delete=models.CASCADE, 
        related_name='watch_parties'
    )
    # Usuario que crea y organiza el watch party
    anfitrion = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='watch_parties_creadas'
    )
    # Usuarios que se han unido al watch party
    participantes = models.ManyToManyField(
        User, 
        related_name='watch_parties_participando', 
        blank=True
    )
    # Nombre descriptivo del watch party
    nombre = models.CharField(max_length=200)
    # Descripción opcional del evento
    descripcion = models.TextField(blank=True)
    # Fecha y hora programada para el evento
    fecha_programada = models.DateTimeField()
    # Fecha de creación del watch party
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    # Estado actual del watch party
    estado = models.CharField(max_length=20, choices=ESTADOS, default='esperando')
    
    # === Control de reproducción sincronizada ===
    # Segundo actual del video (para sincronización)
    tiempo_actual = models.IntegerField(
        default=0, 
        help_text="Segundo actual del video"
    )
    # Indica si el video está reproduciéndose o en pausa
    esta_reproduciendo = models.BooleanField(default=False)
    # Última vez que se actualizó el estado de reproducción
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    # === Configuración del watch party ===
    # Si es público, cualquiera puede unirse
    publico = models.BooleanField(
        default=False, 
        help_text="Si es público, cualquiera puede unirse"
    )
    # Límite máximo de participantes
    max_participantes = models.IntegerField(default=10)
    # Código único para invitaciones privadas
    codigo_invitacion = models.CharField(max_length=20, unique=True, blank=True)
    
    class Meta:
        verbose_name = "Watch Party"
        verbose_name_plural = "Watch Parties"
        # Ordena por fecha programada descendente (más próximos primero)
        ordering = ['-fecha_programada']
    
    def __str__(self):
        return f"{self.nombre} - {self.pelicula.titulo}"
    
    def puede_unirse(self):
        """
        Verifica si hay espacio disponible para más participantes.
        
        Returns:
            bool: True si hay espacio, False si está lleno
        """
        return self.participantes.count() < self.max_participantes
    
    def total_participantes(self):
        """
        Retorna el número total de participantes actuales.
        
        Returns:
            int: Cantidad de participantes
        """
        return self.participantes.count()
    
    def iniciar(self):
        """
        Inicia el watch party cambiando su estado a 'en_curso'.
        """
        self.estado = 'en_curso'
        self.save()
    
    def finalizar(self):
        """
        Finaliza el watch party cambiando su estado a 'finalizada'.
        """
        self.estado = 'finalizada'
        self.save()


class MensajeWatchParty(models.Model):
    """
    Modelo para mensajes del chat durante un Watch Party.
    
    Permite a los participantes chatear en tiempo real mientras
    ven la película juntos.
    """
    # Watch party al que pertenece el mensaje
    watch_party = models.ForeignKey(
        WatchParty, 
        on_delete=models.CASCADE, 
        related_name='mensajes_chat'
    )
    # Usuario que envía el mensaje
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    # Contenido del mensaje de chat
    contenido = models.TextField()
    # Fecha y hora de envío del mensaje
    fecha_envio = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Mensaje de Watch Party"
        verbose_name_plural = "Mensajes de Watch Party"
        # Ordena cronológicamente (ascendente)
        ordering = ['fecha_envio']
    
    def __str__(self):
        # Muestra usuario, nombre del watch party y primeros 30 caracteres
        return f"{self.usuario.username} en {self.watch_party.nombre}: {self.contenido[:30]}"


# ========================
# EXTENSIONES AL MODELO USER
# ========================

# Agrega campo many-to-many para películas favoritas
User.add_to_class(
    'peliculas_favoritas',
    models.ManyToManyField(
        Pelicula,  
        related_name='usuarios_favorito',
        blank=True
    )
)

# Agrega campo many-to-many para películas en lista "ver después"
User.add_to_class(
    'peliculas_ver_despues',
    models.ManyToManyField(
        Pelicula,  
        related_name='usuarios_ver_despues',
        blank=True
    )
)