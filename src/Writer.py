from bs4 import BeautifulSoup
import concurrent.futures
from openpyxl.styles import Alignment, Font
from pandas.core.frame import DataFrame
from .ProgressBar import ProgressBar
from .safe_url import safe_get_url
from .Pelicula import Pelicula
from math import ceil

class Writer(object):
    def __init__(self, id, worksheet):
        # numero de usuario en string
        self.id_user = str(id)
        # Contador de peliculas
        self.film_index = 0
        # Numero de pagina actual
        self.page_index = 1

        # Barra de progreso
        self.bar = ProgressBar()

        # Descargo la propia página actual. Es una página "de fuera".
        self.soup_page = None
        # Lista de peliculas que hay en la página actual
        self.film_list = []

        # Votaciones en total
        self.total_films = self.get_total_films()
        # Rellenar la lista de film_list
        self.get_all_boxes()
        # Hoja de excel
        self.ws = worksheet

    def get_total_films(self):

        url = self.get_list_url(self.page_index)
        resp = safe_get_url(url)
        # Guardo la página ya parseada
        self.soup_page = BeautifulSoup(resp.text,'html.parser')

        # me espero que haya un único "value-box active-tab"
        mydivs = self.soup_page.find("a", {"class": "value-box active-tab"})
        stringNumber = mydivs.contents[3].contents[1]
        # Elimino el punto de los millares
        stringNumber = stringNumber.replace('.','')
        return int(stringNumber)

    def get_all_boxes(self):
        n_pages = ceil(self.total_films / 20)
        url_pages = [self.get_list_url(i + 1) for i in range(n_pages)]

        executor = concurrent.futures.ThreadPoolExecutor()
        self.film_list = list(executor.map(self.list_boxes, url_pages))


    def list_boxes(self, url):
        resp = safe_get_url(url)
        # Guardo la página ya parseada
        soup_page = BeautifulSoup(resp.text,'html.parser')
        # Leo todas las películas que haya en ella
        return list(soup_page.findAll("div", {"class": "user-ratings-movie"}))

    def get_list_url(self, page_index):
        sz_ans = 'https://www.filmaffinity.com/es/userratings.php?user_id=' + self.id_user + '&p='
        sz_ans = sz_ans + str(page_index) + '&orderby=4'

        return sz_ans

    def next_page(self):


        self.film_index += len(self.film_list[self.page_index-1])
        if self.film_index:
            self.bar.update(self.film_index/self.total_films)

        # Anavanzo a la siguiente página
        self.page_index += 1

    def read_watched(self):
        # Creo un objeto para hacer la gestión de paralelización
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=20)
        # Creo una lista de listas donde se guardarán los datos de las películas
        rows_data=[]

        # Creo una barra de progreso
        self.bar.timer.reset()

        # Itero hasta que haya leído todas las películas
        while (self.film_index < self.total_films):
            # Lsita de las películas válidas en la página actual.
            # No puedo modificar self.film_list
            valid_film_list = [Pelicula(box) for box in self.film_list[self.page_index-1]]
            valid_film_list = [film for film in valid_film_list if film.valid()]

            # Itero las películas en mi página actual
            rows_data += list(executor.map(self.read_film, valid_film_list))

            # Avanzo a la siguiente página de películas vistas por el usuario
            self.next_page()

        # Filtro las películas que están suspensas
        rows_data = [row for row in rows_data if row[4] <= 5]
        # Filtro las películas que están aprobadas por mí
        #rows_data = [row for row in rows_data if int(row[1]) >= 6]
        # Ordeno mis votaciones de mayor a menor
        rows_data = list(sorted(rows_data, key=lambda item : item[1], reverse=True))
        df = DataFrame(rows_data,
                        columns=['Id', 'User Note', 'Duration', 'Voters', 'Note FA', 'Title'])

        for index, row in df.iterrows():
            self.write_in_excel(index, row)

    def read_film(self, film : Pelicula):
        # Hacemos la parte más lenta, que necesita parsear la página.
        film.get_time_and_FA()

        # Es importante este orden porque debe coincidir
        # con los encabezados del DataFrame que generaremos
        return [film.id,
                film.user_note,
                film.duracion,
                film.votantes_FA,
                film.nota_FA,
                film.titulo]


    def write_in_excel(self, line, film):

        # La enumeración empezará en 0,
        # pero sólo esribimos datos a partir de la segunda linea.
        line = line + 2

        # La votacion del usuario la leo desde fuera
        # no puedo leer la nota del usuario dentro de la ficha
        UserNote = film['User Note']
        self.set_cell_value(line, 2, int(UserNote))
        self.set_cell_value(line, 10, str("=B" + str(line) + "+RAND()-0.5"))
        self.set_cell_value(line, 11, "=(B" + str(line) + "-1)*10/9")
        # En la primera columna guardo la id para poder reconocerla
        self.set_cell_value(line, 1, film['Title'], int(film['Id']))

        if (film['Duration'] != 0):
            # dejo la casilla en blanco si no logra leer ninguna duración de FA
            self.set_cell_value(line, 4, film['Duration'])
        if (film['Note FA'] != 0):
            # dejo la casilla en blanco si no logra leer ninguna nota de FA
            self.set_cell_value(line, 3, film['Note FA'])
            self.set_cell_value(line, 6, "=ROUND(C" + str(line) + "*2, 0)/2")
            self.set_cell_value(line, 7, "=B" + str(line) + "-C" + str(line))
            self.set_cell_value(line, 8, "=ABS(G" + str(line) + ")")
            self.set_cell_value(line, 9, "=IF($G" + str(line) + ">0,1,0.1)")
            self.set_cell_value(line, 12, "=(C" + str(line) + "-1)*10/9")
        if (film['Voters'] != 0):
            # dejo la casilla en blanco si no logra leer ninguna votantes
            self.set_cell_value(line, 5, film['Voters'])


    def set_cell_value(self, line, col, value, id=0):
        cell = self.ws.cell(row = line, column=col)
        cell.value = value
        # Configuramos el estilo de la celda atendiendo a su columna
        # visionados. Ponemos punto de millar
        if (col == 5):
            cell.number_format = '#,##0'
        # booleano mayor que
        elif (col == 9):
            cell.number_format = '0'
            cell.font = Font(name = 'SimSun', bold = True)
            cell.alignment=Alignment(horizontal='center', vertical='center')
        # Nota del usuario más el ruido
        elif (col == 10):
            cell.number_format = '0.0'
        #reescala
        elif (col == 11 or col == 12):
            cell.number_format = '0.00'
        # Nombre de la película con un hipervínculo
        elif (col == 1):
            # Añado un hipervínculo a su página
            cell.style = 'Hyperlink'
            cell.hyperlink = "https://www.filmaffinity.com/es/film" + str(id) + ".html"
            # Fuerzo el formato como texto
            cell.number_format = '@'

    def next_film(self):
        self.film_index += 1
        self.bar.update(self.film_index/self.total_films)
