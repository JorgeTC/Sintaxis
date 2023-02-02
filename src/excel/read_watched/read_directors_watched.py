from src.excel.film_box import FilmBox
from src.pelicula import Pelicula

from .read_watched import ReadWatched


class ReadDirectorsWatched(ReadWatched):
    def __init__(self, user_id: int) -> None:
        ReadWatched.__init__(self, user_id)

    @staticmethod
    def init_film(movie_box: FilmBox) -> Pelicula:
        instance = Pelicula()

        instance.directors = movie_box.get_directors()
        instance.titulo = movie_box.get_title()
        instance.user_note = movie_box.get_user_note()

        return instance
