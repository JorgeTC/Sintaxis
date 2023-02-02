from concurrent.futures import ThreadPoolExecutor

from src.config import Config, Param, Section
from src.excel.film_box import FilmBox
from src.excel.utils import read_film
from src.pelicula import URL_FILM_ID, Pelicula

from .read_watched import ReadWatched


class ReadDataWatched(ReadWatched):
    def __init__(self, user_id: int) -> None:
        ReadWatched.__init__(self, user_id)

    def read_watched(self, *,
                     use_multithread=Config.get_bool(Section.READDATA, Param.PARALLELIZE)):
        if use_multithread:
            self.read_watched_parallel()
        else:
            ReadWatched.read_watched(self)

    def read_watched_parallel(self) -> None:
        exe = ThreadPoolExecutor(thread_name_prefix="ReadFilm")
        # Incluso aunque no tenga que leer la película la añado al Executor.
        # De lo contrario no se incrementaría la barra de progreso
        futures = (exe.submit(read_film, film) if film
                   else exe.submit(lambda *_: None, film)
                   for film in self.valid_film_list)
        for future in futures:
            future.add_done_callback(self.add_to_queue)
        exe.shutdown(wait=True)
        self.results.put(None)

    @staticmethod
    def init_film(movie_box: FilmBox) -> Pelicula:
        instance = Pelicula()

        # Guardo los valores que conozco por la información introducida
        instance.titulo = movie_box.get_title()
        instance.user_note = movie_box.get_user_note()
        instance.id = movie_box.get_id()
        instance.url_FA = URL_FILM_ID(instance.id)

        # Devuelvo la instancia
        return instance

    @staticmethod
    def read_film(film: Pelicula) -> Pelicula:
        return read_film(film)
