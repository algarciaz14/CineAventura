import requests
from django.conf import settings

class TMDBService:
    """Servicio para interactuar con la API de The Movie Database (TMDB)"""
    
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = settings.TMDB_BASE_URL
        self.image_base_url = settings.TMDB_IMAGE_BASE_URL
    
    def buscar_peliculas(self, query, page=1):
        """
        Busca películas por título
        
        Args:
            query (str): Término de búsqueda
            page (int): Número de página
            
        Returns:
            dict: Resultados de la búsqueda
        """
        url = f"{self.base_url}/search/movie"
        params = {
            'api_key': self.api_key,
            'query': query,
            'language': 'es-MX',
            'page': page,
            'include_adult': False,
            'with_genres': 12 
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al buscar películas: {e}")
            return None
    
    def obtener_detalles_pelicula(self, movie_id):
        """
        Obtiene detalles completos de una película
        
        Args:
            movie_id (int): ID de TMDB de la película
            
        Returns:
            dict: Detalles de la película
        """
        url = f"{self.base_url}/movie/{movie_id}"
        params = {
            'api_key': self.api_key,
            'language': 'es-MX',
            'append_to_response': 'credits,videos'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener detalles: {e}")
            return None
    
    def obtener_peliculas_populares(self, page=1):
        """Obtiene películas populares de AVENTURA
    Args:
        page (int): Número de página
        
    Returns:
        dict: Lista de películas populares de aventura
        """
        url = f"{self.base_url}/discover/movie"  # Cambiado a discover
        params = {
            'api_key': self.api_key,
            'language': 'es-MX',
            'page': page,
            'with_genres': 12,  # ID del género Aventura en TMDB
            'sort_by': 'popularity.desc'
        }
    
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener películas populares: {e}")
            return None
    
    def obtener_peliculas_por_genero(self, genre_id, page=1):
        """
        Obtiene películas por género
        
        Args:
            genre_id (int): ID del género
            page (int): Número de página
            
        Returns:
            dict: Lista de películas del género
        """
        url = f"{self.base_url}/discover/movie"
        params = {
            'api_key': self.api_key,
            'language': 'es-MX',
            'page': page,
            'with_genres': genre_id,
            'sort_by': 'popularity.desc'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener películas por género: {e}")
            return None
    
    def obtener_trailer(self, movie_id):
        """
        Obtiene el trailer de YouTube de una película
        
        Args:
            movie_id (int): ID de TMDB de la película
            
        Returns:
            str: URL del trailer de YouTube o None
        """
        detalles = self.obtener_detalles_pelicula(movie_id)
        
        if detalles and 'videos' in detalles:
            videos = detalles['videos']['results']
            
            # Buscar trailer oficial en español
            for video in videos:
                if video['type'] == 'Trailer' and video['site'] == 'YouTube':
                    if 'es' in video.get('iso_639_1', '').lower():
                        return f"https://www.youtube.com/watch?v={video['key']}"
            
            # Si no hay en español, buscar cualquier trailer
            for video in videos:
                if video['type'] == 'Trailer' and video['site'] == 'YouTube':
                    return f"https://www.youtube.com/watch?v={video['key']}"
        
        return None
    
    def obtener_poster_url(self, poster_path):
        """
        Construye la URL completa del póster
        
        Args:
            poster_path (str): Path del póster desde TMDB
            
        Returns:
            str: URL completa del póster o None
        """
        if poster_path:
            return f"{self.image_base_url}{poster_path}"
        return None
    
    def formatear_pelicula_para_db(self, movie_data):
        """
        Formatea los datos de TMDB al formato de tu base de datos
        
        Args:
            movie_data (dict): Datos de la película desde TMDB
            
        Returns:
            dict: Datos formateados para tu modelo
        """
        # Obtener detalles completos
        detalles = self.obtener_detalles_pelicula(movie_data['id'])
        
        if not detalles:
            return None
        
        # Obtener trailer
        trailer_url = self.obtener_trailer(movie_data['id'])
        
        # Formatear fecha de estreno
        fecha_estreno = detalles.get('release_date', '')
        año = int(fecha_estreno.split('-')[0]) if fecha_estreno else 2024
        
        # Obtener director (primer director del crew)
        director_nombre = None
        if 'credits' in detalles and 'crew' in detalles['credits']:
            for crew_member in detalles['credits']['crew']:
                if crew_member['job'] == 'Director':
                    director_nombre = crew_member['name']
                    break
        
        # Obtener actores principales (primeros 5)
        actores = []
        if 'credits' in detalles and 'cast' in detalles['credits']:
            actores = [actor['name'] for actor in detalles['credits']['cast'][:5]]
        
        # Datos formateados
        return {
            'titulo': detalles.get('title', movie_data.get('title', 'Sin título')),
            'titulo_original': detalles.get('original_title', ''),
            'sinopsis': detalles.get('overview', 'Sin sinopsis disponible'),
            'año': año,
            'duracion': detalles.get('runtime', 0),
            'pais': detalles.get('production_countries', [{}])[0].get('name', 'Desconocido') if detalles.get('production_countries') else 'Desconocido',
            'idioma': detalles.get('original_language', 'es').upper(),
            'poster': self.obtener_poster_url(detalles.get('poster_path')),
            'trailer': trailer_url,
            'fecha_estreno': fecha_estreno or '2024-01-01',
            'presupuesto': detalles.get('budget', 0),
            'recaudacion': detalles.get('revenue', 0),
            'generos_ids': [g['id'] for g in detalles.get('genres', [])],
            'generos_nombres': [g['name'] for g in detalles.get('genres', [])],
            'director_nombre': director_nombre,
            'actores_nombres': actores,
            'tmdb_id': movie_data['id'],
            'popularidad': movie_data.get('popularity', 0),
            'vote_average': movie_data.get('vote_average', 0)
        }


# Diccionario de mapeo de géneros TMDB a tus géneros locales
GENRE_MAPPING = {
    28: 'Acción',          # Action
    12: 'Aventura',        # Adventure
    35: 'Comedia',         # Comedy
    18: 'Drama',           # Drama
    27: 'Terror',          # Horror
    878: 'Ciencia Ficción', # Science Fiction
    14: 'Fantasía',        # Fantasy
    10749: 'Romance'       # Romance
}