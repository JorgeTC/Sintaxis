from concurrent.futures import ThreadPoolExecutor
from random import randint
from typing import Iterable, Optional

from src.config import Config, Param, Section
from src.excel.utils import is_valid, read_film
from src.pelicula import Pelicula


class RandomFilmId:
    def __init__(self) -> None:
        self.ids = list(range(100_000, 1_000_000))
        self.size = len(self.ids)

    def get_id(self) -> int:

        if self.size == 0:
            return 0

        self.size -= 1
        rand_index = randint(0, self.size)
        self.ids[self.size], self.ids[rand_index] = self.ids[rand_index], self.ids[self.size]

        return self.ids.pop()

    def get_ids_lot(self, lot_size: int) -> Iterable[int]:
        lot_size = min(lot_size, self.size)
        return (self.get_id() for _ in range(lot_size))


def read_sample(*,
                use_multithread=Config.get_bool(Section.READDATA, Param.PARALLELIZE)) -> Iterable[Pelicula]:
    # Creo un objeto para hacer la gestión de paralelización
    executor = ThreadPoolExecutor(max_workers=50)

    # Creo un generador aleatorio de ids de películas
    rnd = RandomFilmId()

    while rnd.size:
        # Lista de las películas válidas en la página actual.
        film_list = (Pelicula.from_id(id)
                     for id in rnd.get_ids_lot(125))

        # Itero las películas en mi página actual
        if use_multithread:
            iter_film_data = executor.map(
                read_film_if_valid, film_list)
        else:
            iter_film_data = (read_film_if_valid(film)
                              for film in film_list)

        for film_data in iter_film_data:
            if film_data and film_data.nota_FA:
                yield film_data


def read_film_if_valid(film: Pelicula) -> Optional[Pelicula]:

    # Si la película no es válida no devuelvo nada
    if not has_valid_id(film):
        return None

    # Es válida, devuelvo la película con los datos rellenos
    try:
        return read_film(film)
    except:
        return None


def has_valid_id(film: Pelicula) -> bool:

    # Parseo la página.
    film.get_parsed_page()
    # compruebo si la página obtenida existe
    if not film.exists():
        return False

    # Obtengo el título de la película...
    try:
        film.get_title()
    except:
        return False
    # ...para comprobar si es válido
    if not is_valid(film):
        return False

    # Compruebo por último que tenga nota media
    film.get_nota_FA()
    if not film.nota_FA:
        return False

    # Si el id es válido, el título es válido y tiene nota en FA, es un id válido para mi estadística
    return True
