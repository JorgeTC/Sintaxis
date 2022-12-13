import re
from concurrent.futures import ThreadPoolExecutor
from math import ceil
from typing import Iterable

from bs4 import BeautifulSoup, Tag

import src.url_FA as url_FA
from src.config import Config, Param, Section
from src.excel.utils import is_valid, read_film
from src.pelicula import Pelicula
from src.safe_url import safe_get_url


def read_watched(id_user: int, *,
                 use_multithread=Config.get_bool(Section.READDATA, Param.PARALLELIZE)) -> Iterable[tuple[Pelicula, float]]:

    # Votaciones en total
    total_films = get_total_films(id_user)

    # Creo un objeto para hacer la gestión de paralelización
    executor = ThreadPoolExecutor(max_workers=20)

    # Lista de todas las cajas de películas del usuario
    film_list = get_all_boxes(id_user, total_films)
    # Contador de películas leídas
    film_index = 0

    # Itero hasta que haya leído todas las películas
    for page_boxes in film_list:
        # Lista de las películas válidas en la página actual.
        films_in_page = (init_film_from_movie_box(box)
                         for box in page_boxes)
        valid_film_list = (film for film in films_in_page
                           if is_valid(film))

        # Itero las películas en mi página actual
        if use_multithread:
            iter_film_data = executor.map(read_film, valid_film_list)
        else:
            iter_film_data = (read_film(film) for film in valid_film_list)

        read_in_page = 0
        for film_data in iter_film_data:
            read_in_page += 1
            yield film_data, (film_index + read_in_page)/total_films

        # Avanzo a la siguiente página de películas vistas por el usuario
        film_index = min(film_index + 20, total_films)


def read_directors(id_user: int) -> Iterable[tuple[Pelicula, float]]:
    # Votaciones en total
    total_films = get_total_films(id_user)

    # Lista de todas las cajas de películas del usuario
    film_list = get_all_boxes(id_user, total_films)
    # Contador de películas leídas
    film_index = 0

    # Itero hasta que haya leído todas las películas
    for page_boxes in film_list:
        # Lista de las películas válidas en la página actual.
        films_in_page = (init_director_from_movie_box(box)
                         for box in page_boxes)
        valid_film_list = (film for film in films_in_page
                           if is_valid(film))

        read_in_page = 0
        for film_data in valid_film_list:
            read_in_page += 1
            yield film_data, (film_index + read_in_page)/total_films

        # Avanzo a la siguiente página de películas vistas por el usuario
        film_index = min(film_index + 20, total_films)


def get_total_films(id_user: int) -> int:

    url = url_FA.URL_USER_PAGE(id_user, 1)
    resp = safe_get_url(url)
    # Guardo la página ya parseada
    soup_page = BeautifulSoup(resp.text, 'lxml')

    # me espero que haya un único "value-box active-tab"
    mydivs = soup_page.find("a", {"class": "value-box active-tab"})
    stringNumber = str(mydivs.contents[3].contents[1])
    # Elimino el punto de los millares
    stringNumber = stringNumber.replace('.', '')
    return int(stringNumber)


def get_all_boxes(user_id: int, total_films: int) -> Iterable[Iterable[BeautifulSoup]]:
    n_pages = ceil(total_films / 20)
    url_pages = (url_FA.URL_USER_PAGE(user_id, i + 1)
                 for i in range(n_pages))

    executor = ThreadPoolExecutor()
    return executor.map(list_boxes, url_pages)


def list_boxes(url: str) -> Iterable[BeautifulSoup]:
    resp = safe_get_url(url)
    # Guardo la página ya parseada
    soup_page = BeautifulSoup(resp.text, 'lxml')
    # Leo todas las películas que haya en ella
    return soup_page.findAll("div", {"class": "user-ratings-movie"})


class FromFilmBox:
    '''Funciones para extraer datos de la caja de la película'''
    @staticmethod
    def get_title(film_box: BeautifulSoup) -> str:
        return film_box.contents[1].contents[1].contents[3].contents[1].contents[0].contents[0]

    @staticmethod
    def get_user_note(film_box: BeautifulSoup) -> int:
        return int(film_box.contents[3].contents[1].contents[1].contents[0])

    @staticmethod
    def get_id(film_box: BeautifulSoup) -> int:
        return int(film_box.contents[1].contents[1].attrs['data-movie-id'])

    @staticmethod
    def get_year(film_box: BeautifulSoup) -> int:
        str_year = str(
            film_box.contents[1].contents[1].contents[3].contents[1].contents[1])
        return int(re.search(r"(\d{4})", str_year).group(1))

    @staticmethod
    def get_country(film_box: BeautifulSoup) -> str:
        return film_box.contents[1].contents[1].contents[3].contents[1].contents[2].attrs['alt']

    @staticmethod
    def get_directors(film_box: BeautifulSoup) -> str:
        try:
            directors = film_box.contents[1].contents[1].contents[3].contents[5].contents[1].contents
        except IndexError:
            return ''
        return [director.contents[0].contents[0]
                for director in directors
                if isinstance(director, Tag)]

    @staticmethod
    def get_director(film_box: BeautifulSoup) -> str:
        try:
            return FromFilmBox.get_directors(film_box)[0]
        except IndexError:
            return ''


def init_film_from_movie_box(movie_box: BeautifulSoup) -> Pelicula:
    instance = Pelicula()

    # Guardo los valores que conozco por la información introducida
    instance.titulo = FromFilmBox.get_title(movie_box)
    instance.user_note = FromFilmBox.get_user_note(movie_box)
    instance.id = FromFilmBox.get_id(movie_box)
    instance.url_FA = url_FA.URL_FILM_ID(instance.id)

    # Devuelvo la instancia
    return instance


def init_director_from_movie_box(movie_box: BeautifulSoup) -> Pelicula:
    instance = Pelicula()

    instance.directors = FromFilmBox.get_directors(movie_box)
    instance.titulo = FromFilmBox.get_title(movie_box)

    return instance
