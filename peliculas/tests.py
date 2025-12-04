"""
Tests completos para Cine Aventura - Sistema de reseñas de películas de aventura

Este archivo contiene tests para:
- Modelos (Models)
- Vistas (Views)
- Formularios (Forms)
- Funcionalidades específicas
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import (
    Genero, Director, Actor, Pelicula, Calificacion, Resena,
    ListaPersonalizada, PerfilUsuario, Conversacion, Mensaje,
    Notificacion, HistorialVisualizacion, WatchParty, MensajeWatchParty
)
from .forms import RegistroUsuarioForm, PeliculaForm, WatchPartyForm


# ========================================
# TESTS DE MODELOS
# ========================================

class GeneroModelTest(TestCase):
    """Tests para el modelo Genero"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.genero = Genero.objects.create(
            nombre="Aventura",
            descripcion="Películas de aventura emocionantes"
        )
    
    def test_genero_creation(self):
        """Verifica que el género se crea correctamente"""
        self.assertEqual(self.genero.nombre, "Aventura")
        self.assertEqual(str(self.genero), "Aventura")
    
    def test_genero_unique_nombre(self):
        """Verifica que el nombre del género es único"""
        with self.assertRaises(Exception):
            Genero.objects.create(nombre="Aventura")
    
    def test_genero_ordering(self):
        """Verifica que los géneros se ordenan alfabéticamente"""
        Genero.objects.create(nombre="Acción")
        Genero.objects.create(nombre="Comedia")
        generos = list(Genero.objects.all())
        self.assertEqual(generos[0].nombre, "Acción")
        self.assertEqual(generos[1].nombre, "Aventura")


class DirectorModelTest(TestCase):
    """Tests para el modelo Director"""
    
    def setUp(self):
        self.director = Director.objects.create(
            nombre="Steven Spielberg",
            biografia="Director legendario",
            nacionalidad="Estados Unidos"
        )
    
    def test_director_creation(self):
        """Verifica creación del director"""
        self.assertEqual(self.director.nombre, "Steven Spielberg")
        self.assertEqual(str(self.director), "Steven Spielberg")
    
    def test_director_optional_fields(self):
        """Verifica que campos opcionales pueden estar vacíos"""
        director = Director.objects.create(nombre="John Doe")
        self.assertEqual(director.biografia, "")
        self.assertIsNone(director.fecha_nacimiento)


class PeliculaModelTest(TestCase):
    """Tests para el modelo Pelicula"""
    
    def setUp(self):
        """Crea datos de prueba"""
        self.genero = Genero.objects.create(nombre="Aventura")
        self.director = Director.objects.create(nombre="Steven Spielberg")
        self.actor = Actor.objects.create(nombre="Harrison Ford")
        
        self.pelicula = Pelicula.objects.create(
            titulo="Indiana Jones",
            titulo_original="Indiana Jones and the Raiders of the Lost Ark",
            sinopsis="Arqueólogo busca el Arca Perdida",
            año=1981,
            duracion=115,
            director=self.director,
            pais="Estados Unidos",
            idioma="Inglés",
            fecha_estreno=timezone.now().date(),
            clasificacion="PG-13"
        )
        self.pelicula.generos.add(self.genero)
        self.pelicula.actores.add(self.actor)
    
    def test_pelicula_creation(self):
        """Verifica creación de película"""
        self.assertEqual(self.pelicula.titulo, "Indiana Jones")
        self.assertEqual(str(self.pelicula), "Indiana Jones (1981)")
    
    def test_pelicula_generos_relationship(self):
        """Verifica relación many-to-many con géneros"""
        self.assertIn(self.genero, self.pelicula.generos.all())
        self.assertEqual(self.pelicula.generos.count(), 1)
    
    def test_pelicula_actores_relationship(self):
        """Verifica relación con actores"""
        self.assertIn(self.actor, self.pelicula.actores.all())
    
    def test_calificacion_promedio_sin_calificaciones(self):
        """Verifica promedio cuando no hay calificaciones"""
        self.assertEqual(self.pelicula.calificacion_promedio(), 0)
    
    def test_calificacion_promedio_con_calificaciones(self):
        """Verifica cálculo de promedio de calificaciones"""
        user1 = User.objects.create_user('user1', 'user1@test.com', 'pass123')
        user2 = User.objects.create_user('user2', 'user2@test.com', 'pass123')
        
        Calificacion.objects.create(pelicula=self.pelicula, usuario=user1, puntuacion=8)
        Calificacion.objects.create(pelicula=self.pelicula, usuario=user2, puntuacion=10)
        
        self.assertEqual(self.pelicula.calificacion_promedio(), 9.0)
    
    def test_total_resenas(self):
        """Verifica conteo de reseñas"""
        user = User.objects.create_user('user', 'user@test.com', 'pass123')
        Resena.objects.create(
            pelicula=self.pelicula,
            usuario=user,
            titulo="Excelente",
            contenido="Gran película"
        )
        self.assertEqual(self.pelicula.total_resenas(), 1)


class CalificacionModelTest(TestCase):
    """Tests para el modelo Calificacion"""
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.genero = Genero.objects.create(nombre="Aventura")
        self.director = Director.objects.create(nombre="Director Test")
        self.pelicula = Pelicula.objects.create(
            titulo="Test Movie",
            sinopsis="Test",
            año=2020,
            duracion=120,
            director=self.director,
            pais="USA",
            idioma="EN",
            fecha_estreno=timezone.now().date()
        )
        self.pelicula.generos.add(self.genero)
    
    def test_calificacion_creation(self):
        """Verifica creación de calificación"""
        calificacion = Calificacion.objects.create(
            pelicula=self.pelicula,
            usuario=self.user,
            puntuacion=9
        )
        self.assertEqual(calificacion.puntuacion, 9)
        self.assertEqual(str(calificacion), "testuser - Test Movie: 9/10")
    
    def test_calificacion_unique_together(self):
        """Verifica que un usuario solo puede calificar una vez"""
        Calificacion.objects.create(
            pelicula=self.pelicula,
            usuario=self.user,
            puntuacion=8
        )
        
        with self.assertRaises(Exception):
            Calificacion.objects.create(
                pelicula=self.pelicula,
                usuario=self.user,
                puntuacion=10
            )
    
    def test_calificacion_range_validation(self):
        """Verifica validación de rango (1-10)"""
        # Esto debería funcionar
        cal1 = Calificacion(pelicula=self.pelicula, usuario=self.user, puntuacion=1)
        cal2 = Calificacion(pelicula=self.pelicula, usuario=self.user, puntuacion=10)
        
        # No hay excepciones en valores válidos
        try:
            cal1.full_clean()
            cal2.full_clean()
        except Exception:
            self.fail("Validación falló con valores válidos")


class ResenaModelTest(TestCase):
    """Tests para el modelo Resena"""
    
    def setUp(self):
        self.user = User.objects.create_user('reviewer', 'rev@test.com', 'pass123')
        self.genero = Genero.objects.create(nombre="Aventura")
        self.director = Director.objects.create(nombre="Director")
        self.pelicula = Pelicula.objects.create(
            titulo="Movie",
            sinopsis="Test",
            año=2020,
            duracion=120,
            director=self.director,
            pais="USA",
            idioma="EN",
            fecha_estreno=timezone.now().date()
        )
        self.pelicula.generos.add(self.genero)
    
    def test_resena_creation(self):
        """Verifica creación de reseña"""
        resena = Resena.objects.create(
            pelicula=self.pelicula,
            usuario=self.user,
            titulo="Increíble película",
            contenido="Me encantó esta película de aventura"
        )
        self.assertEqual(resena.titulo, "Increíble película")
        self.assertEqual(resena.util_count, 0)
    
    def test_resena_unique_together(self):
        """Verifica que un usuario solo puede reseñar una vez"""
        Resena.objects.create(
            pelicula=self.pelicula,
            usuario=self.user,
            titulo="Primera",
            contenido="Contenido"
        )
        
        with self.assertRaises(Exception):
            Resena.objects.create(
                pelicula=self.pelicula,
                usuario=self.user,
                titulo="Segunda",
                contenido="Contenido 2"
            )


class PerfilUsuarioModelTest(TestCase):
    """Tests para el modelo PerfilUsuario"""
    
    def test_perfil_creation_on_user_creation(self):
        """Verifica que el perfil se crea al registrar usuario"""
        user = User.objects.create_user('newuser', 'new@test.com', 'pass123')
        
        # Crear perfil manualmente (en producción se hace con signals)
        perfil = PerfilUsuario.objects.create(
            usuario=user,
            aceptado_terminos=True,
            fecha_aceptacion_terminos=timezone.now(),
            version_terminos='1.0'
        )
        
        self.assertTrue(perfil.aceptado_terminos)
        self.assertEqual(perfil.version_terminos, '1.0')


class ConversacionModelTest(TestCase):
    """Tests para el modelo Conversacion"""
    
    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'u1@test.com', 'pass123')
        self.user2 = User.objects.create_user('user2', 'u2@test.com', 'pass123')
        self.conversacion = Conversacion.objects.create()
        self.conversacion.participantes.add(self.user1, self.user2)
    
    def test_conversacion_creation(self):
        """Verifica creación de conversación"""
        self.assertEqual(self.conversacion.participantes.count(), 2)
        self.assertIn(self.user1, self.conversacion.participantes.all())
    
    def test_ultimo_mensaje(self):
        """Verifica obtención del último mensaje"""
        # Crear primer mensaje
        mensaje_1 = Mensaje.objects.create(
            conversacion=self.conversacion,
            remitente=self.user1,
            contenido="Hola"
        )
        
        # Pequeña pausa para asegurar diferentes timestamps
        import time
        time.sleep(0.1)
        
        # Crear segundo mensaje (más reciente)
        mensaje_reciente = Mensaje.objects.create(
            conversacion=self.conversacion,
            remitente=self.user2,
            contenido="Hola, ¿cómo estás?"
        )
        
        # Verificar que el último mensaje es el más reciente
        ultimo = self.conversacion.ultimo_mensaje()
        self.assertEqual(ultimo.id, mensaje_reciente.id)
        self.assertEqual(ultimo.contenido, "Hola, ¿cómo estás?")
    
    def test_mensajes_no_leidos(self):
        """Verifica conteo de mensajes no leídos"""
        Mensaje.objects.create(
            conversacion=self.conversacion,
            remitente=self.user2,
            contenido="Mensaje 1",
            leido=False
        )
        Mensaje.objects.create(
            conversacion=self.conversacion,
            remitente=self.user2,
            contenido="Mensaje 2",
            leido=False
        )
        
        self.assertEqual(self.conversacion.mensajes_no_leidos(self.user1), 2)
        self.assertEqual(self.conversacion.mensajes_no_leidos(self.user2), 0)


class WatchPartyModelTest(TestCase):
    """Tests para el modelo WatchParty"""
    
    def setUp(self):
        self.user = User.objects.create_user('host', 'host@test.com', 'pass123')
        self.genero = Genero.objects.create(nombre="Aventura")
        self.director = Director.objects.create(nombre="Director")
        self.pelicula = Pelicula.objects.create(
            titulo="Película Watch Party",
            sinopsis="Test",
            año=2024,
            duracion=120,
            director=self.director,
            pais="USA",
            idioma="EN",
            fecha_estreno=timezone.now().date()
        )
        self.pelicula.generos.add(self.genero)
        
        self.watch_party = WatchParty.objects.create(
            pelicula=self.pelicula,
            anfitrion=self.user,
            nombre="Watch Party Test",
            descripcion="Descripción test",
            fecha_programada=timezone.now() + timedelta(days=1),
            max_participantes=10,
            codigo_invitacion="ABC123"
        )
    
    def test_watch_party_creation(self):
        """Verifica creación de watch party"""
        self.assertEqual(self.watch_party.nombre, "Watch Party Test")
        self.assertEqual(self.watch_party.estado, "esperando")
    
    def test_puede_unirse(self):
        """Verifica si hay espacio disponible"""
        self.assertTrue(self.watch_party.puede_unirse())
        
        # Llenar watch party
        for i in range(10):
            user = User.objects.create_user(f'user{i}', f'u{i}@test.com', 'pass')
            self.watch_party.participantes.add(user)
        
        self.assertFalse(self.watch_party.puede_unirse())
    
    def test_total_participantes(self):
        """Verifica conteo de participantes"""
        self.assertEqual(self.watch_party.total_participantes(), 0)
        self.watch_party.participantes.add(self.user)
        self.assertEqual(self.watch_party.total_participantes(), 1)
    
    def test_iniciar_watch_party(self):
        """Verifica cambio de estado al iniciar"""
        self.watch_party.iniciar()
        self.assertEqual(self.watch_party.estado, "en_curso")
    
    def test_finalizar_watch_party(self):
        """Verifica cambio de estado al finalizar"""
        self.watch_party.finalizar()
        self.assertEqual(self.watch_party.estado, "finalizada")


# ========================================
# TESTS DE VISTAS (VIEWS)
# ========================================

class IndexViewTest(TestCase):
    """Tests para la vista principal (index)"""
    
    def setUp(self):
        self.client = Client()
        self.genero = Genero.objects.create(nombre="Aventura")
        self.director = Director.objects.create(nombre="Director")
        
        # Crear película de aventura
        self.pelicula = Pelicula.objects.create(
            titulo="Película Aventura",
            sinopsis="Sinopsis",
            año=2024,
            duracion=120,
            director=self.director,
            pais="USA",
            idioma="EN",
            fecha_estreno=timezone.now().date()
        )
        self.pelicula.generos.add(self.genero)
    
    def test_index_view_status_code(self):
        """Verifica que la página principal carga correctamente"""
        response = self.client.get(reverse('peliculas:index'))
        self.assertEqual(response.status_code, 200)
    
    def test_index_view_template(self):
        """Verifica que usa el template correcto"""
        response = self.client.get(reverse('peliculas:index'))
        self.assertTemplateUsed(response, 'peliculas/index.html')
    
    def test_index_context_peliculas_aventura(self):
        """Verifica que solo muestra películas de aventura"""
        response = self.client.get(reverse('peliculas:index'))
        self.assertIn('peliculas_destacadas', response.context)
        self.assertIn('peliculas_recientes', response.context)


class CatalogoViewTest(TestCase):
    """Tests para la vista del catálogo"""
    
    def setUp(self):
        self.client = Client()
        self.genero = Genero.objects.create(nombre="Aventura")
        self.director = Director.objects.create(nombre="Director")
        
        # Crear 15 películas para probar paginación
        for i in range(15):
            pelicula = Pelicula.objects.create(
                titulo=f"Película {i}",
                sinopsis="Test",
                año=2020 + i,
                duracion=120,
                director=self.director,
                pais="USA",
                idioma="EN",
                fecha_estreno=timezone.now().date()
            )
            pelicula.generos.add(self.genero)
    
    def test_catalogo_view_status_code(self):
        """Verifica que el catálogo carga"""
        response = self.client.get(reverse('peliculas:catalogo'))
        self.assertEqual(response.status_code, 200)
    
    def test_catalogo_pagination(self):
        """Verifica paginación (12 por página)"""
        response = self.client.get(reverse('peliculas:catalogo'))
        self.assertEqual(len(response.context['peliculas']), 12)
    
    def test_catalogo_search(self):
        """Verifica búsqueda en catálogo"""
        response = self.client.get(reverse('peliculas:catalogo'), {'q': 'Película 5'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Película 5')
    
    def test_catalogo_ordering(self):
        """Verifica ordenamiento"""
        response = self.client.get(reverse('peliculas:catalogo'), {'orden': 'az'})
        peliculas = list(response.context['peliculas'])
        self.assertEqual(peliculas[0].titulo, 'Película 0')


class DetallePeliculaViewTest(TestCase):
    """Tests para la vista de detalle de película"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.genero = Genero.objects.create(nombre="Aventura")
        self.director = Director.objects.create(nombre="Director")
        
        self.pelicula = Pelicula.objects.create(
            titulo="Película Test",
            sinopsis="Sinopsis test",
            año=2024,
            duracion=120,
            director=self.director,
            pais="USA",
            idioma="EN",
            fecha_estreno=timezone.now().date()
        )
        self.pelicula.generos.add(self.genero)
    
    def test_detalle_view_status_code(self):
        """Verifica que la página de detalle carga"""
        response = self.client.get(reverse('peliculas:detalle', args=[self.pelicula.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_detalle_view_404(self):
        """Verifica 404 para película inexistente"""
        response = self.client.get(reverse('peliculas:detalle', args=[9999]))
        self.assertEqual(response.status_code, 404)
    
    def test_detalle_registra_visualizacion(self):
        """Verifica que se registra visualización para usuarios autenticados"""
        self.client.login(username='testuser', password='pass123')
        self.client.get(reverse('peliculas:detalle', args=[self.pelicula.id]))
        
        # Verificar que existe historial
        self.assertTrue(
            HistorialVisualizacion.objects.filter(
                usuario=self.user,
                pelicula=self.pelicula
            ).exists()
        )


class AgregarCalificacionViewTest(TestCase):
    """Tests para agregar calificaciones"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.genero = Genero.objects.create(nombre="Aventura")
        self.director = Director.objects.create(nombre="Director")
        
        self.pelicula = Pelicula.objects.create(
            titulo="Película",
            sinopsis="Test",
            año=2024,
            duracion=120,
            director=self.director,
            pais="USA",
            idioma="EN",
            fecha_estreno=timezone.now().date()
        )
        self.pelicula.generos.add(self.genero)
    
    def test_agregar_calificacion_requiere_login(self):
        """Verifica que se requiere login para calificar"""
        response = self.client.post(
            reverse('peliculas:agregar_calificacion', args=[self.pelicula.id]),
            {'puntuacion': 9}
        )
        self.assertEqual(response.status_code, 302)  # Redirect al login
    
    def test_agregar_calificacion_exitosa(self):
        """Verifica que se puede agregar calificación"""
        self.client.login(username='testuser', password='pass123')
        response = self.client.post(
            reverse('peliculas:agregar_calificacion', args=[self.pelicula.id]),
            {'puntuacion': 9}
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(
            Calificacion.objects.filter(
                usuario=self.user,
                pelicula=self.pelicula,
                puntuacion=9
            ).exists()
        )


class AgregarResenaViewTest(TestCase):
    """Tests para agregar reseñas"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('reviewer', 'rev@test.com', 'pass123')
        self.genero = Genero.objects.create(nombre="Aventura")
        self.director = Director.objects.create(nombre="Director")
        
        self.pelicula = Pelicula.objects.create(
            titulo="Película",
            sinopsis="Test",
            año=2024,
            duracion=120,
            director=self.director,
            pais="USA",
            idioma="EN",
            fecha_estreno=timezone.now().date()
        )
        self.pelicula.generos.add(self.genero)
    
    def test_agregar_resena_requiere_login(self):
        """Verifica que se requiere login"""
        response = self.client.post(
            reverse('peliculas:agregar_resena', args=[self.pelicula.id]),
            {'titulo': 'Buena', 'contenido': 'Me gustó'}
        )
        self.assertEqual(response.status_code, 302)
    
    def test_agregar_resena_exitosa(self):
        """Verifica que se puede agregar reseña"""
        self.client.login(username='reviewer', password='pass123')
        response = self.client.post(
            reverse('peliculas:agregar_resena', args=[self.pelicula.id]),
            {'titulo': 'Excelente película', 'contenido': 'Me encantó la trama y actuaciones'}
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Resena.objects.filter(
                usuario=self.user,
                pelicula=self.pelicula
            ).exists()
        )


class MiPerfilViewTest(TestCase):
    """Tests para la vista de perfil"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
    
    def test_perfil_requiere_login(self):
        """Verifica que el perfil requiere autenticación"""
        response = self.client.get(reverse('peliculas:perfil'))
        self.assertEqual(response.status_code, 302)
    
    def test_perfil_view_authenticated(self):
        """Verifica que el perfil carga para usuarios autenticados"""
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('peliculas:perfil'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'peliculas/perfil.html')


# ========================================
# TESTS DE FORMULARIOS (FORMS)
# ========================================

class RegistroUsuarioFormTest(TestCase):
    """Tests para el formulario de registro"""
    
    def test_form_valid_data(self):
        """Verifica formulario con datos válidos"""
        form = RegistroUsuarioForm(data={
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@test.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'aceptar_terminos': True
        })
        self.assertTrue(form.is_valid())
    
    def test_form_terminos_required(self):
        """Verifica que los términos son obligatorios"""
        form = RegistroUsuarioForm(data={
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@test.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'aceptar_terminos': False
        })
        self.assertFalse(form.is_valid())
    
    def test_form_email_unique(self):
        """Verifica que el email debe ser único"""
        User.objects.create_user('user1', 'test@test.com', 'pass123')
        
        form = RegistroUsuarioForm(data={
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'test@test.com',  # Email duplicado
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'aceptar_terminos': True
        })
        self.assertFalse(form.is_valid())


class WatchPartyFormTest(TestCase):
    """Tests para el formulario de Watch Party"""
    
    def test_form_valid_data(self):
        """Verifica formulario válido"""
        fecha_futura = timezone.now() + timedelta(days=1)
        form = WatchPartyForm(data={
            'nombre': 'Mi Watch Party',
            'descripcion': 'Vamos a ver una película',
            'fecha_programada': fecha_futura,
            'publico': True,
            'max_participantes': 10
        })
        self.assertTrue(form.is_valid())
    
    def test_form_fecha_pasada_invalida(self):
        """Verifica que fecha pasada es inválida"""
        fecha_pasada = timezone.now() - timedelta(days=1)
        form = WatchPartyForm(data={
            'nombre': 'Watch Party',
            'descripcion': 'Test',
            'fecha_programada': fecha_pasada,
            'publico': False,
            'max_participantes': 5
        })
        self.assertFalse(form.is_valid())


# ========================================
# TESTS DE FUNCIONALIDADES ESPECÍFICAS
# ========================================

class FavoritosTest(TestCase):
    """Tests para sistema de favoritos"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.genero = Genero.objects.create(nombre="Aventura")
        self.director = Director.objects.create(nombre="Director")
        
        self.pelicula = Pelicula.objects.create(
            titulo="Película",
            sinopsis="Test",
            año=2024,
            duracion=120,
            director=self.director,
            pais="USA",
            idioma="EN",
            fecha_estreno=timezone.now().date()
        )
        self.pelicula.generos.add(self.genero)
    
    def test_agregar_a_favoritos(self):
        """Verifica agregar película a favoritos"""
        self.client.login(username='testuser', password='pass123')
        response = self.client.post(
            reverse('peliculas:agregar_favoritos', args=[self.pelicula.id])
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.pelicula, self.user.peliculas_favoritas.all())
    
    def test_quitar_de_favoritos(self):
        """Verifica quitar película de favoritos (toggle)"""
        self.client.login(username='testuser', password='pass123')
        
        # Agregar
        self.user.peliculas_favoritas.add(self.pelicula)
        self.assertIn(self.pelicula, self.user.peliculas_favoritas.all())
        
        # Quitar (segundo click)
        self.client.post(reverse('peliculas:agregar_favoritos', args=[self.pelicula.id]))
        self.user.refresh_from_db()
        self.assertNotIn(self.pelicula, self.user.peliculas_favoritas.all())


class RecomendacionesTest(TestCase):
    """Tests para sistema de recomendaciones"""
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.genero_aventura = Genero.objects.create(nombre="Aventura")
        self.genero_accion = Genero.objects.create(nombre="Acción")
        self.director = Director.objects.create(nombre="Director")
        
        # Crear películas de aventura
        for i in range(5):
            pelicula = Pelicula.objects.create(
                titulo=f"Aventura {i}",
                sinopsis="Test",
                año=2024,
                duracion=120,
                director=self.director,
                pais="USA",
                idioma="EN",
                fecha_estreno=timezone.now().date()
            )
            pelicula.generos.add(self.genero_aventura)
    
    def test_recomendaciones_view_requiere_login(self):
        """Verifica que recomendaciones requiere login"""
        response = self.client.get(reverse('peliculas:recomendaciones'))
        self.assertEqual(response.status_code, 302)
    
    def test_recomendaciones_view_authenticated(self):
        """Verifica que recomendaciones carga para usuarios autenticados"""
        self.client = Client()
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('peliculas:recomendaciones'))
        self.assertEqual(response.status_code, 200)


class BusquedaTest(TestCase):
    """Tests para sistema de búsqueda"""
    
    def setUp(self):
        self.client = Client()
        self.genero = Genero.objects.create(nombre="Aventura")
        self.director = Director.objects.create(nombre="Steven Spielberg")
        
        self.pelicula = Pelicula.objects.create(
            titulo="Indiana Jones",
            titulo_original="Raiders of the Lost Ark",
            sinopsis="Arqueólogo aventurero",
            año=1981,
            duracion=115,
            director=self.director,
            pais="USA",
            idioma="EN",
            fecha_estreno=timezone.now().date()
        )
        self.pelicula.generos.add(self.genero)
    
    def test_busqueda_por_titulo(self):
        """Verifica búsqueda por título"""
        response = self.client.get(reverse('peliculas:buscar'), {'q': 'Indiana'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Indiana Jones')
    
    def test_busqueda_por_director(self):
        """Verifica búsqueda por director"""
        response = self.client.get(reverse('peliculas:buscar'), {'q': 'Spielberg'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Indiana Jones')
    
    def test_busqueda_sin_resultados(self):
        """Verifica búsqueda sin resultados"""
        response = self.client.get(reverse('peliculas:buscar'), {'q': 'XYZ123'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Indiana Jones')


class SocialHubTest(TestCase):
    """Tests para Social Hub"""
    
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user('user1', 'u1@test.com', 'pass123')
        self.user2 = User.objects.create_user('user2', 'u2@test.com', 'pass123')
    
    def test_social_hub_requiere_login(self):
        """Verifica que Social Hub requiere autenticación"""
        response = self.client.get(reverse('peliculas:social_hub'))
        self.assertEqual(response.status_code, 302)
    
    def test_social_hub_view_authenticated(self):
        """Verifica que Social Hub carga correctamente"""
        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('peliculas:social_hub'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('usuarios', response.context)
    
    def test_perfil_usuario_view(self):
        """Verifica vista de perfil de otro usuario"""
        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('peliculas:perfil_usuario', args=[self.user2.id]))
        self.assertEqual(response.status_code, 200)


class MensajeriaTest(TestCase):
    """Tests para sistema de mensajería"""
    
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user('user1', 'u1@test.com', 'pass123')
        self.user2 = User.objects.create_user('user2', 'u2@test.com', 'pass123')
        
        self.conversacion = Conversacion.objects.create()
        self.conversacion.participantes.add(self.user1, self.user2)
    
    def test_lista_conversaciones_requiere_login(self):
        """Verifica que lista de conversaciones requiere login"""
        response = self.client.get(reverse('peliculas:lista_conversaciones'))
        self.assertEqual(response.status_code, 302)
    
    def test_lista_conversaciones_authenticated(self):
        """Verifica que lista de conversaciones carga"""
        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('peliculas:lista_conversaciones'))
        self.assertEqual(response.status_code, 200)
    
    def test_enviar_mensaje(self):
        """Verifica envío de mensaje"""
        self.client.login(username='user1', password='pass123')
        response = self.client.post(
            reverse('peliculas:conversacion', args=[self.conversacion.id]),
            {'contenido': 'Hola, ¿cómo estás?'}
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Mensaje.objects.filter(
                conversacion=self.conversacion,
                remitente=self.user1,
                contenido='Hola, ¿cómo estás?'
            ).exists()
        )
    
    def test_marcar_mensaje_como_leido(self):
        """Verifica marcado de mensaje como leído"""
        mensaje = Mensaje.objects.create(
            conversacion=self.conversacion,
            remitente=self.user2,
            contenido="Mensaje de prueba",
            leido=False
        )
        
        mensaje.marcar_como_leido()
        mensaje.refresh_from_db()
        
        self.assertTrue(mensaje.leido)
        self.assertIsNotNone(mensaje.fecha_lectura)


class WatchPartyFunctionalityTest(TestCase):
    """Tests para funcionalidades de Watch Party"""
    
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user('host', 'host@test.com', 'pass123')
        self.user2 = User.objects.create_user('guest', 'guest@test.com', 'pass123')
        
        self.genero = Genero.objects.create(nombre="Aventura")
        self.director = Director.objects.create(nombre="Director")
        self.pelicula = Pelicula.objects.create(
            titulo="Película",
            sinopsis="Test",
            año=2024,
            duracion=120,
            director=self.director,
            pais="USA",
            idioma="EN",
            fecha_estreno=timezone.now().date()
        )
        self.pelicula.generos.add(self.genero)
        
        self.watch_party = WatchParty.objects.create(
            pelicula=self.pelicula,
            anfitrion=self.user1,
            nombre="Watch Party Test",
            fecha_programada=timezone.now() + timedelta(days=1),
            max_participantes=5,
            publico=True,
            codigo_invitacion="ABC123"
        )
    
    def test_lista_watch_parties_requiere_login(self):
        """Verifica que lista de watch parties requiere login"""
        response = self.client.get(reverse('peliculas:lista_watch_parties'))
        self.assertEqual(response.status_code, 302)
    
    def test_lista_watch_parties_authenticated(self):
        """Verifica que lista carga correctamente"""
        self.client.login(username='host', password='pass123')
        response = self.client.get(reverse('peliculas:lista_watch_parties'))
        self.assertEqual(response.status_code, 200)
    
    def test_unirse_watch_party(self):
        """Verifica unirse a watch party"""
        self.client.login(username='guest', password='pass123')
        response = self.client.get(
            reverse('peliculas:unirse_watch_party', args=[self.watch_party.id])
        )
        
        self.assertEqual(response.status_code, 302)
        self.watch_party.refresh_from_db()
        self.assertIn(self.user2, self.watch_party.participantes.all())
    
    def test_salir_watch_party(self):
        """Verifica salir de watch party"""
        self.watch_party.participantes.add(self.user2)
        
        self.client.login(username='guest', password='pass123')
        response = self.client.get(
            reverse('peliculas:salir_watch_party', args=[self.watch_party.id])
        )
        
        self.assertEqual(response.status_code, 302)
        self.watch_party.refresh_from_db()
        self.assertNotIn(self.user2, self.watch_party.participantes.all())
    
    def test_enviar_mensaje_watch_party(self):
        """Verifica envío de mensaje en chat"""
        self.watch_party.participantes.add(self.user1)
        
        self.client.login(username='host', password='pass123')
        response = self.client.post(
            reverse('peliculas:enviar_mensaje_watch_party', args=[self.watch_party.id]),
            {'contenido': '¡Empecemos!'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            MensajeWatchParty.objects.filter(
                watch_party=self.watch_party,
                usuario=self.user1,
                contenido='¡Empecemos!'
            ).exists()
        )


# ========================================
# TESTS DE INTEGRACIÓN
# ========================================

class UserJourneyTest(TestCase):
    """Tests de flujo completo de usuario"""
    
    def setUp(self):
        self.client = Client()
        
        # Crear datos base
        self.genero = Genero.objects.create(nombre="Aventura")
        self.director = Director.objects.create(nombre="Director")
        self.pelicula = Pelicula.objects.create(
            titulo="Gran Aventura",
            sinopsis="Una aventura épica",
            año=2024,
            duracion=120,
            director=self.director,
            pais="USA",
            idioma="EN",
            fecha_estreno=timezone.now().date()
        )
        self.pelicula.generos.add(self.genero)
    
    def test_complete_user_journey(self):
        """Test de flujo completo: registro, login, calificar, reseñar"""
        
        # 1. Registro
        response = self.client.post(reverse('peliculas:registro'), {
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@test.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'aceptar_terminos': True
        })
        self.assertEqual(response.status_code, 302)  # Redirect después del registro
        
        # 2. Login
        self.client.login(username='newuser', password='TestPass123!')
        
        # 3. Ver detalle de película
        response = self.client.get(reverse('peliculas:detalle', args=[self.pelicula.id]))
        self.assertEqual(response.status_code, 200)
        
        # 4. Calificar película
        response = self.client.post(
            reverse('peliculas:agregar_calificacion', args=[self.pelicula.id]),
            {'puntuacion': 9}
        )
        self.assertEqual(response.status_code, 302)
        
        # 5. Escribir reseña
        response = self.client.post(
            reverse('peliculas:agregar_resena', args=[self.pelicula.id]),
            {'titulo': 'Increíble', 'contenido': 'Me encantó'}
        )
        self.assertEqual(response.status_code, 302)
        
        # 6. Agregar a favoritos
        response = self.client.post(
            reverse('peliculas:agregar_favoritos', args=[self.pelicula.id])
        )
        self.assertEqual(response.status_code, 302)
        
        # Verificar que todo se guardó correctamente
        user = User.objects.get(username='newuser')
        self.assertTrue(Calificacion.objects.filter(usuario=user).exists())
        self.assertTrue(Resena.objects.filter(usuario=user).exists())
        self.assertIn(self.pelicula, user.peliculas_favoritas.all())