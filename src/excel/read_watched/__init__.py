from typing import Iterator

from src.pelicula import Pelicula

from .read_data_watched import ReadDataWatched
from .read_directors_watched import ReadDirectorsWatched


def read_directors(id_user: int) -> Iterator[tuple[Pelicula, float]]:
    reader = ReadDirectorsWatched(id_user)
    for film in reader.iter():
        yield film, reader.proportion


def read_data(id_user: int) -> Iterator[tuple[Pelicula, float]]:
    reader = ReadDataWatched(id_user)
    for film in reader.iter():
        yield film, reader.proportion


__all__ = [read_directors, read_data]
