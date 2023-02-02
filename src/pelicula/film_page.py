import re
from typing import Optional
from bs4 import BeautifulSoup

from src.safe_url import safe_get_url

# Cómo debo buscar la información de las barras
RATING_BARS_PATTERN = re.compile(r'RatingBars.*?\[(.*?)\]')


class FilmPage:
    def __init__(self, url_FA: str) -> None:
        self.parsed_page = get_parsed_page(url_FA)

    def get_año(self) -> int:
        l = self.parsed_page.find(itemprop="datePublished")
        return int(l.contents[0])

    def get_votantes_FA(self) -> int:
        # Me espero que la página ya haya sido parseada
        l = self.parsed_page.find(itemprop="ratingCount")
        try:
            # guardo la cantidad de votantes en una ficha normal
            voters_str = l.attrs['content']
            # Elimino el punto de los millares
            voters_str = voters_str.replace('.', '')
            return int(voters_str)
        except:
            # caso en el que no hay suficientes votantes
            return 0

    def get_duracion(self):
        # Me espero que la página ya haya sido parseada
        l = self.parsed_page.find(id="left-column")
        try:
            str_duracion = l.find(itemprop="duration").contents[0]
            str_duracion = re.search(r'(\d+) +min.', str_duracion).group(1)
            return int(str_duracion)
        except:
            # caso en el que no está escrita la duración
            return 0

    def get_country(self) -> str:
        try:
            return self.parsed_page.find(
                id="country-img").contents[0].attrs['alt']
        except:
            return ""

    def get_title(self) -> str:
        l = self.parsed_page.find(itemprop="name")
        return l.contents[0]

    def get_director(self) -> list[str]:
        tag_directors = self.parsed_page.find_all(itemprop="director")
        return [tag.contents[0].contents[0].contents[0]
                for tag in tag_directors]

    def get_values(self) -> list[int]:
        # Recopilo los datos específicos de la varianza:
        script = self.parsed_page.find("script", string=RATING_BARS_PATTERN)
        if not script:
            return []

        # Extraigo cuánto vale cada barra
        bars = RATING_BARS_PATTERN.search(script.string).group(1)
        values = [int(s) for s in bars.split(',')]
        # Las ordeno poniendo primero las notas más bajas
        values.reverse()
        # Me aseguro que todos los datos sean positivos
        return [max(value, 0) for value in values]

    def get_image_url(self):
        return self.parsed_page.find(
            "meta", property="og:image")['content']

    def get_avg_note(self) -> float:
        search_avg = self.parsed_page.find(id="movie-rat-avg")
        try:
            return float(search_avg.attrs['content'])
        except AttributeError:
            return 0

    @property
    def exists(self):
        return self.parsed_page is not None


def get_parsed_page(url_FA: str) -> Optional[BeautifulSoup]:
    resp = safe_get_url(url_FA)
    if resp.status_code == 404:
        # Si el id no es correcto, no tengo página que parsear
        return None

    # Parseo la página
    return BeautifulSoup(resp.text, 'lxml')
