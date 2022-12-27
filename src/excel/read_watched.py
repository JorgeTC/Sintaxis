from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps
from math import ceil
from typing import Callable, Iterable

from bs4 import BeautifulSoup

import src.url_FA as url_FA
from src.config import Config, Param, Section
from src.excel.film_box import FilmBox
from src.excel.utils import is_valid, read_film
from src.pelicula import Pelicula
from src.safe_url import safe_get_url


def transform_user_data(f: Callable[[Iterable[FilmBox], ...], Iterable[Pelicula | None]]):
    '''
    Se aplica a funciones cuyo primer argumento es `box_list: Iterable[FilmBox]`
    '''

    @wraps(f)
    def wrp(id_user: int, *args, **kwargs):
        extract_data = partial(f, *args, **kwargs)
        return read_user_data(id_user, extract_data)

    return wrp


@transform_user_data
def read_watched(box_list: Iterable[FilmBox], *,
                 use_multithread=Config.get_bool(Section.READDATA, Param.PARALLELIZE)) -> Iterable[Pelicula | None]:

    # Lista de las películas válidas en la página actual.
    films_list = (init_film_from_movie_box(box) for box in box_list)
    valid_film_list = (film if is_valid(film) else None for film in films_list)

    # Itero las películas en mi página actual
    iter_film_data = ThreadPoolExecutor().map(read_film, valid_film_list) if use_multithread \
        else (read_film(film) for film in valid_film_list)

    return iter_film_data


@transform_user_data
def read_directors(box_list: Iterable[FilmBox]) -> Iterable[Pelicula | None]:
    # Lista de las películas válidas en la página actual.
    films_list = (init_director_from_movie_box(box) for box in box_list)
    return (film if is_valid(film) else None for film in films_list)


def read_user_data(id_user: int, f: Callable[[Iterable[FilmBox]], Iterable[Pelicula | None]]) -> Iterable[tuple[Pelicula, float]]:
    # Votaciones en total
    total_films = get_total_films(id_user)

    # Lista de todas las cajas de películas del usuario
    box_list = get_all_boxes(id_user, total_films)

    for film_index, film_data in enumerate(f(box_list)):
        if film_data is not None:
            yield film_data, film_index / total_films


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


def get_all_boxes(user_id: int, total_films: int) -> Iterable[FilmBox]:
    for films_in_page in get_all_pages_boxes(user_id, total_films):
        for box in films_in_page:
            yield box


def get_all_pages_boxes(user_id: int, total_films: int) -> Iterable[Iterable[FilmBox]]:
    n_pages = ceil(total_films / 20)
    url_pages = (url_FA.URL_USER_PAGE(user_id, i + 1)
                 for i in range(n_pages))

    executor = ThreadPoolExecutor()
    return executor.map(list_boxes, url_pages)


def list_boxes(url: str) -> Iterable[FilmBox]:
    resp = safe_get_url(url)
    # Guardo la página ya parseada
    soup_page = BeautifulSoup(resp.text, 'lxml')
    # Leo todas las películas que haya en ella
    return [FilmBox(parsed_box) for parsed_box in soup_page.findAll("div", {"class": "user-ratings-movie"})]


def init_film_from_movie_box(movie_box: FilmBox) -> Pelicula:
    instance = Pelicula()

    # Guardo los valores que conozco por la información introducida
    instance.titulo = movie_box.get_title()
    instance.user_note = movie_box.get_user_note()
    instance.id = movie_box.get_id()
    instance.url_FA = url_FA.URL_FILM_ID(instance.id)

    # Devuelvo la instancia
    return instance


def init_director_from_movie_box(movie_box: FilmBox) -> Pelicula:
    instance = Pelicula()

    instance.directors = movie_box.get_directors()
    instance.titulo = movie_box.get_title()

    return instance
