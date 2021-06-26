import requests
import webbrowser
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font
# from openpyxl.styles import PatternFill, Border, Side, numbers
import sys
from bs4 import BeautifulSoup
import time
import datetime

class Timer(object):
    def __init__(self):
        self.start = datetime.datetime.now()

    def remains(self, done):
        if done != 0:
            now  = datetime.datetime.now()
            left = (1 - done) * (now - self.start) / done
            sec = int(left.total_seconds())
            if sec < 60:
                return "{} seconds   ".format(sec)
            else:
                return "{} minutes   ".format(int(sec / 60))

class ProgressBar(object):
    def __init__(self):
        self.timer = Timer()
        self.barLength = 20
        self.progress = 0.0

    def update(self, done):
        self.progress = float(done)
        block = int(round(self.barLength * self.progress))
        text = "\r[{0}] {1:.2f}% {2}".format( "="*block + " "*(self. barLength-block), self. progress*100, self.timer.remains(self.progress))
        sys.stdout.write(text)
        sys.stdout.flush()

class Pelicula(object):
    def __init__(self, urlFA = None):
            self.url_FA = str(urlFA)
            resp = SafeGetUrl(self.get_FA_url())
            if resp.status_code == 404:
                self.exists = False
                return # Si el id no es correcto, dejo de construir la clase
            else:
                self.exists = True

            # Parseo la página
            self.parsed_page = BeautifulSoup(resp.text,'html.parser')

            self.nota_FA = None
            self.votantes_FA = None
            self.duracion = None

    def get_FA_url(self):
        return self.url_FA

    def GetTimeAndFA(self):
        # Comienzo a leer datos de la página
        l = self.parsed_page.find(id="movie-rat-avg")
        try:
            # guardo la nota de FA en una ficha normal
            self.nota_FA = float(l.attrs['content'])
        except:
            # caso en el que no hay nota de FA
            self.nota_FA = 0

        l = self.parsed_page.find(itemprop="ratingCount")
        try:
            # guardo la cantidad de votantes en una ficha normal
            self.votantes_FA = l.attrs['content']
            # Elimino el punto de los millares
            self.votantes_FA = self.votantes_FA.replace('.','')
            self.votantes_FA = int(self.votantes_FA)
        except:
            # caso en el que no hay suficientes votantes
            self.votantes_FA = 0

        l = self.parsed_page.find(id = "left-column")
        try:
            self.duracion = l.find(itemprop="duration").contents[0]
        except:
            # caso en el que no está escrita la duración
            self.duracion = "0"
        # quito el sufijo min.
        self.duracion = int(self.duracion.split(' ', 1)[0])

def es_valida(titulo):
    """
    Busca en el título que sea una película realmente
    """
    # Comprobamos que no tenga ninuno de los sufijos a evitar
    if titulo.find("(C)") > 0: # Excluyo los cortos
        return False
    if titulo.find("(Miniserie de TV)") > 0: # Excluyo series de televisión
        return False
    if titulo.find("(Serie de TV)") > 0:
        return False
    if titulo.find("(TV)") > 0:
        # Hay varios tipos de películas aquí.
        # Algunos son programas de televisón, otros estrenos directos a tele.
        # Hay también episosios concretos de series.
        return False
    if titulo.find("(Vídeo musical)") > 0:
        return False
    # No se ha encontrado sufijo, luego es una película
    return True

class IndexLine():
    # Esta clase debería ser capaz de dar cualquier orden a las películas
    def __init__(self, totales):
        self.m_totales = totales
        # Hay que inicializarlo para que no escriba en los encabezados
        self.m_current = 2

    def GetCurrentLine(self):
        # Actualizo el valor
        self.m_current += 1
        # Devuelvo el valor antes de haberlo actualizado
        return self.m_current - 1

def get_url_from_id(id):
    """
    Me espero el id en cadena, por si acaso hago la conversión
    """
    return 'https://www.filmaffinity.com/es/film' + str(id) + ".html"

def SafeGetUrl(url):
    #open with GET method
    resp = requests.get(url)
    # Caso 429: too many requests
    if resp.status_code == 429:
        return PassCaptcha(url)
    else: # No está contemplado el caso 404: not found
        return resp

def PassCaptcha(url):
    # abro un navegador para poder pasar el Captcha
    webbrowser.open(url)
    resp = requests.get(url)
    print("\nPor favor, entra en FilmAffinity y pasa el captcha por mí.")
    # Controlo que se haya pasado el Captcha
    while resp.status_code != 200:
        time.sleep(3) # intento recargar la página cada 3 segundos
        resp = requests.get(url)
    return resp

def set_cell_value(ws, line, col, value):
    cell = ws.cell(row = line, column=col)
    cell.value = value
    # Configuramos el estilo de la celda
    if (col == 5): # visionados. Ponemos punto de millar
        cell.number_format = '#,##0'
    elif (col == 9): # booleano mayor que
        cell.number_format = '0'
        cell.font = Font(name = 'SimSun', bold = True)
        cell.alignment=Alignment(horizontal='center', vertical='center')
    elif (col == 10):
        cell.number_format = '0.0'
    elif (col == 11 or col == 12): #reescala
        cell.number_format = '0.00'

def GetTotalFilms(resp):
    soup=BeautifulSoup(resp.text,'html.parser')
    # me espero que haya un único "value-box active-tab"
    mydivs = soup.find("a", {"class": "value-box active-tab"})
    stringNumber = mydivs.contents[3].contents[1]
    # Elimino el punto de los millares
    stringNumber = stringNumber.replace('.','')
    return int(stringNumber)

def IndexToLine(index, total):
    return total - index + 1


def ReadWatched(IdUser, ws):
    DataIndex = 0 # contador de peliculas
    nIndex = 1 # numero de pagina actual
    Vistas = 'https://www.filmaffinity.com/es/userratings.php?user_id=' + str(IdUser) + '&p=' + str(nIndex) + '&orderby=4'
    resp = SafeGetUrl(Vistas)

    totalFilms = GetTotalFilms(resp)
    Iline = IndexLine(totalFilms) # linea de excel en la que estoy escribiendo
    line = Iline.GetCurrentLine()
    bar = ProgressBar()
    while (DataIndex < totalFilms):

        # we need a parser,Python built-in HTML parser is enough .
        soup = BeautifulSoup(resp.text,'html.parser')
        # Guardo en una lista todas las películas de la página nIndex-ésima
        mylist = soup.findAll("div", {"class": "user-ratings-movie"})

        for i in mylist:
            titulo =  i.contents[1].contents[1].contents[3].contents[1].contents[0].contents[0]

            if not es_valida(titulo):
                DataIndex +=1
                continue

            # La votacion del usuario la leo desde fuera
            # no puedo leer la nota del usuario dentro de la ficha
            UserNote = i.contents[3].contents[1].contents[1].contents[0]
            set_cell_value(ws, line, 2, int(UserNote))
            set_cell_value(ws, line, 10, str("=B" + str(line) + "+RAND()-0.5"))
            set_cell_value(ws, line, 11, "=(B" + str(line) + "-1)*10/9")
            # En la primera columna guardo la id para poder reconocerla
            n_id = i.contents[1].contents[1].attrs['data-movie-id']
            set_cell_value(ws, line, 1, int(n_id))
            #guardo la url de la ficha de la pelicula
            url = get_url_from_id(n_id)
            #Entro a la ficha y leo votacion popular, duracion y votantes
            pelicula = Pelicula(urlFA = url)
            pelicula.GetTimeAndFA()
            if (pelicula.duracion != 0):
                # dejo la casilla en blanco si no logra leer ninguna duración de FA
                set_cell_value(ws, line, 4, pelicula.duracion)
            if (pelicula.nota_FA != 0):
                # dejo la casilla en blanco si no logra leer ninguna nota de FA
                set_cell_value(ws, line, 3, pelicula.nota_FA)
                set_cell_value(ws, line, 6, "=ROUND(C" + str(line) + "*2, 0)/2")
                set_cell_value(ws, line, 7, "=B" + str(line) + "-C" + str(line))
                set_cell_value(ws, line, 8, "=ABS(G" + str(line) + ")")
                set_cell_value(ws, line, 9, "=IF($G" + str(line) + ">0,1,0.1)")
                set_cell_value(ws, line, 12, "=(C" + str(line) + "-1)*10/9")
            if (pelicula.votantes_FA != 0):
                # dejo la casilla en blanco si no logra leer ninguna votantes
                set_cell_value(ws, line, 5, pelicula.votantes_FA)
            DataIndex +=1
            # actualizo la barra de progreso
            bar.update(DataIndex/totalFilms)
            # actualizo la linea de escritura en excel
            line = Iline.GetCurrentLine()

        # Siguiente pagina del listado
        nIndex += 1
        Vistas = 'https://www.filmaffinity.com/es/userratings.php?user_id=' + str(IdUser) + '&p=' + str(nIndex) + '&orderby=4'
        resp = SafeGetUrl(Vistas)

def get_user():
    Ids = {'Sasha': 1230513, 'Jorge': 1742789, 'Guillermo': 4627260, 'Daniel Gallego': 983049, 'Luminador': 7183467,
    'Will_llermo': 565861, 'Roger Peris': 3922745, 'Javi': 247783, 'El Feo': 867335, 'coleto': 527264}
    usuario = 'Jorge'
    print("Se van a importar los datos de ", usuario)
    inp = input("Espero Enter...")
    if inp and inp in Ids.keys():
        usuario = inp
        print("Se van a importar los datos de ", usuario)

    return usuario, Ids[usuario]


if __name__ == "__main__":
    usuario, id = get_user()
    Plantilla = 'Plantilla.xlsx'
    ExcelName = 'Sintaxis - ' + usuario + '.xlsx'
    workbook = load_workbook(Plantilla)
    worksheet = workbook[workbook.sheetnames[0]]
    ReadWatched(id, worksheet)
    workbook.save(ExcelName)
    workbook.close()
