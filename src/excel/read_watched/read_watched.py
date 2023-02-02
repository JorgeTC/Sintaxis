from concurrent.futures import Future
from math import ceil
from queue import Queue
from threading import Thread
from typing import Iterable

from bs4 import BeautifulSoup

from src.excel.film_box import FilmBox
from src.excel.utils import is_valid
from src.pelicula import Pelicula
from src.safe_url import safe_get_url


class ReadWatched:
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        self.results: Queue[Pelicula] = Queue()
        self.total_films = get_total_films(self.user_id)
        self.box_list = get_all_boxes(self.user_id, self.total_films)
        self.index = -1

        Thread(target=self.read_watched).start()

    @property
    def proportion(self) -> float:
        return (self.index + 1) / self.total_films

    @property
    def valid_film_list(self) -> Iterable[Pelicula | None]:
        # Lista de las películas válidas en la página actual.
        films_list = (self.init_film(box) for box in self.box_list)
        valid_film_list = (film if is_valid(film) else None
                           for film in films_list)

        return valid_film_list

    def read_watched(self) -> None:
        # Iteración convencional de valid_film_list
        for self.index, film in enumerate(self.valid_film_list):
            # Si la película no es None, la leo
            if film is not None:
                self.results.put(self.read_film(film))

        # Añado un None para saber cuándo he acabado la iteración
        self.results.put(None)

    def iter(self) -> Iterable[Pelicula]:
        while (film := self.results.get()):
            yield film

    def add_to_queue(self, result: Future):
        self.index += 1
        if (film := result.result()):
            self.results.put(film)

    @staticmethod
    def init_film(box: FilmBox) -> Pelicula:
        raise NotImplementedError

    @staticmethod
    def read_film(film: Pelicula) -> Pelicula:
        return film


# Link para acceder a cada página de un usuario
URL_USER_PAGE = 'https://www.filmaffinity.com/es/userratings.php?user_id={}&p={}&orderby=4'.format


def get_total_films(id_user: int) -> int:

    url = URL_USER_PAGE(id_user, 1)
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
    n_pages = ceil(total_films / 20)
    url_pages = (URL_USER_PAGE(user_id, i + 1)
                 for i in range(n_pages))

    # Itero todas las páginas del actual usuario
    for page in url_pages:
        # Itero la página actual
        for box in list_boxes(page):
            yield box


def list_boxes(url: str) -> Iterable[FilmBox]:
    resp = safe_get_url(url)
    # Guardo la página ya parseada
    soup_page = BeautifulSoup(resp.text, 'lxml')
    # Leo todas las películas que haya en ella
    return (FilmBox(parsed_box) for parsed_box in
            soup_page.findAll("div", {"class": "user-ratings-movie"}))
