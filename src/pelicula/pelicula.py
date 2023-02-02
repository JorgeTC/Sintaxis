import math
import re
from functools import wraps

from src.pelicula.film_page import FilmPage


def get_id_from_url(url: str) -> int:
    # Cojo los 6 dígitos que están después de la palabra film
    str_id = re.search(r"film(\d{6}).html", url).group(1)

    return int(str_id)


def scrap_data(att: str):
    '''
    Decorador para obtener datos parseados de la página.
    Comprueba que no se haya ya leído el dato para evitar redundancia.
    Comprueba antes de buscar en la página que ya esté parseada.
    '''
    def decorator(fn):
        @wraps(fn)
        def wrp(self: 'Pelicula', *args, **kwarg):
            # Si ya tengo guardado el dato que se me pide, no busco nada más
            if getattr(self, att) is not None:
                return

            # Antes de obtener el dato me aseguro de que la página haya sido parseada
            if not self.film_page:
                self.get_parsed_page()

            fn(self, *args, **kwarg)
        return wrp
    return decorator


def check_votes(att: str):
    '''
    Decorador para obtener cálculos de las votaciones.
    Comprueba que ya tenga los votos
    '''
    def decorator(fn):
        @wraps(fn)
        def wrp(self: 'Pelicula', *args, **kwarg):
            # Compruebo que haya leído los votos de la película
            if self.values is None:
                self.get_values()

            # Si a pesar de haberlos buscado no he conseguido los votos, no puedo saber su nota
            # por lo tanto no puedo calcular el atributo actual
            if not self.values:
                setattr(self, att, 0)
                return

            # Tengo los datos que necesito para calcular el atributo en cuestión
            fn(self, *args, **kwarg)
        return wrp
    return decorator


def scrap_from_values(att: str):
    '''
    Concatena el decorador para no calcular un atributo dos veces
    y el decorador para comprobar que se tienen los valores
    '''
    def decorator(fn):
        # Aplico primero el decorador para evitar calcular el atributo dos veces.
        # Una vez que sé que tengo que estoy obligado a calcular el atributo,
        # compruebo que la lista de valores esté calculada.
        return scrap_data(att)(check_votes(att)(fn))
    return decorator


URL_FILM_ID = "https://www.filmaffinity.com/es/film{}.html".format


class Pelicula:
    def __init__(self):

        self.titulo: str = None
        self.user_note: int = None
        self.id: int = None
        self.url_FA: str = None
        self.url_image: str = None
        self.film_page: FilmPage = None
        self.nota_FA: float = None
        self.votantes_FA: int = None
        self.desvest_FA: float = None
        self.prop_aprobados: float = None
        self.values: list[int] = None
        self.duracion: int = None
        self.directors: list[str] = None
        self.año: int = None
        self.pais: str = None

    @classmethod
    def from_id(cls, id: int) -> 'Pelicula':
        # Creo el objeto
        instance = cls()

        # Guardo los valores que conozco por la información introducida
        instance.id = int(id)
        instance.url_FA = URL_FILM_ID(instance.id)

        # Devuelvo la instancia
        return instance

    @classmethod
    def from_fa_url(cls, urlFA: str) -> 'Pelicula':
        # Creo el objeto
        instance = cls()

        # Guardo los valores que conozco por la información introducida
        instance.url_FA = str(urlFA)
        instance.id = get_id_from_url(instance.url_FA)

        # Devuelvo la instancia
        return instance

    @scrap_from_values('nota_FA')
    def get_nota_FA(self):
        self.nota_FA = 0
        # Multiplico la nota por la cantidad de gente que la ha dado
        for vote, quantity in enumerate(self.values):
            self.nota_FA += (vote + 1) * quantity
        # Divido entre el número total
        self.nota_FA /= sum(self.values)

    @scrap_data('votantes_FA')
    def get_votantes_FA(self):
        self.votantes_FA = self.film_page.get_votantes_FA()

    @scrap_data('duracion')
    def get_duracion(self):
        self.duracion = self.film_page.get_duracion()

    @scrap_data('pais')
    def get_country(self):
        self.pais = self.film_page.get_country()

    @scrap_data('titulo')
    def get_title(self):
        self.titulo = self.film_page.get_title()

    def get_parsed_page(self):
        self.film_page = FilmPage(self.url_FA)

    @scrap_data('directors')
    def get_director(self):
        self.directors = self.film_page.get_director()

    @scrap_data('año')
    def get_año(self):
        self.año = self.film_page.get_año()

    @scrap_data('values')
    def get_values(self):
        self.values = self.film_page.get_values()

    @scrap_data('url_image')
    def get_image_url(self):
        self.url_image = self.film_page.get_image_url()

    @scrap_from_values('desvest_FA')
    def get_desvest(self):

        # Me aseguro que se haya tratado de calcular la nota
        if self.nota_FA is None:
            self.get_nota_FA()

        # Calculo la varianza
        varianza = 0
        # Itero las frecuencias.
        # Cada frecuencia representa a la puntuación igual a su posición en la lista más 1
        for note, votes in enumerate(self.values):
            varianza += votes * ((note + 1 - self.nota_FA) ** 2)
        varianza /= sum(self.values)

        # Doy el valor a la variable miembro, lo convierto a desviación típica
        self.desvest_FA = math.sqrt(varianza)

    @scrap_from_values('prop_aprobados')
    def get_prop_aprobados(self):
        # Cuento cuántos votos positivos hay
        positives = sum(self.values[5:])
        # Cuento cuántos votos hay en total
        total_votes = sum(self.values)
        # Calculo la proporción
        self.prop_aprobados = positives / total_votes

    def exists(self) -> bool:
        return self.film_page.exists

    @property
    def director(self) -> str:
        if self.directors is None:
            return None
        try:
            return self.directors[0]
        except IndexError:
            return ''

    @director.setter
    def director(self, value: str):
        self.directors = [value]
