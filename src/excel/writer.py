import enum

from openpyxl.cell import Cell
from openpyxl.styles import Alignment, Font
from openpyxl.worksheet import worksheet

from src.excel.read_sample import read_sample
from src.excel.read_watched import read_data
from src.pelicula import URL_FILM_ID, Pelicula
from src.gui import ProgressBar


class ExcelColumns(int, enum.Enum):
    Id = enum.auto()
    Mia = enum.auto()
    FA = enum.auto()
    Duracion = enum.auto()
    Visionados = enum.auto()
    Varianza_FA = enum.auto()
    Prop_aprobados_FA = enum.auto()
    FA_redondeo = enum.auto()
    Diferencia = enum.auto()
    Diferencia_abs = enum.auto()
    Me_ha_gustado = enum.auto()
    Mia_ruido = enum.auto()
    FA_ruido = enum.auto()
    Mia_rees = enum.auto()
    FA_rees = enum.auto()

    def __str__(self) -> str:
        return f"Tabla1[{self.name}]"


class Writer:

    def __init__(self, worksheet: worksheet.Worksheet):
        # Barra de progreso
        self.bar = ProgressBar()

        # Hoja de excel
        self.ws = worksheet

    def write_sample(self, sample_size: int) -> None:
        # Creo una barra de progreso
        bar = ProgressBar()

        # Número de películas leídas
        row = 0

        # Itero hasta que haya leído todas las películas
        for film_data in read_sample():
            self.__write_in_excel(row, film_data)
            row += 1

            # Actualizo la barra de progreso
            bar.update(row / sample_size)

            # Si ya tengo suficientes películas, salgo del bucle
            if row >= sample_size:
                break

    def write_watched(self, id_user: int):

        # Inicializo la fila actual en la que estoy escribiendo
        index = 0
        bar = ProgressBar()
        for film_data, progress in read_data(id_user):
            self.__write_in_excel(index, film_data)
            index += 1
            bar.update(progress)

    def __write_in_excel(self, line: int, film: Pelicula):

        # La enumeración empezará en 0,
        # pero sólo escribimos datos a partir de la segunda linea.
        line = line + 2

        # En la primera columna guardo la id para poder reconocerla
        self.__set_cell_value(line, ExcelColumns.Id,
                              film.titulo, id=film.id)

        # La votación del usuario la leo desde fuera
        # no puedo leer la nota del usuario dentro de la ficha
        if (film.user_note):
            self.__set_cell_value(line, ExcelColumns.Mia,
                                  film.user_note)
            self.__set_cell_value(line, ExcelColumns.Mia_ruido,
                                  f"={ExcelColumns.Mia}+RAND()-0.5")
            self.__set_cell_value(line, ExcelColumns.Mia_rees,
                                  f"=({ExcelColumns.Mia}-1)*10/9")

        if (film.duracion != 0):
            # dejo la casilla en blanco si no logra leer ninguna duración de FA
            self.__set_cell_value(line, ExcelColumns.Duracion,
                                  film.duracion)

        if (film.nota_FA != 0):
            # dejo la casilla en blanco si no logra leer ninguna nota de FA
            self.__set_cell_value(line, ExcelColumns.FA,
                                  film.nota_FA)
            self.__set_cell_value(line, ExcelColumns.FA_redondeo,
                                  f"=ROUND({ExcelColumns.FA}*2, 0)/2")
            self.__set_cell_value(line, ExcelColumns.Diferencia,
                                  f"={ExcelColumns.Mia}-{ExcelColumns.FA}")
            self.__set_cell_value(line, ExcelColumns.Diferencia_abs,
                                  f"=ABS({ExcelColumns.Diferencia})")
            self.__set_cell_value(line, ExcelColumns.Me_ha_gustado,
                                  f"=IF({ExcelColumns.Diferencia}>0,1,0.1)")
            self.__set_cell_value(line, ExcelColumns.FA_rees,
                                  f"=({ExcelColumns.FA}-1)*10/9")
            self.__set_cell_value(line, ExcelColumns.FA_ruido,
                                  f"={ExcelColumns.FA}+(RAND()-0.5)/10")

        if (film.votantes_FA != 0):
            # dejo la casilla en blanco si no logra leer ninguna votantes
            self.__set_cell_value(line, ExcelColumns.Visionados,
                                  film.votantes_FA)

        if (film.desvest_FA != 0):
            self.__set_cell_value(line, ExcelColumns.Varianza_FA,
                                  film.desvest_FA)
            self.__set_cell_value(line, ExcelColumns.Prop_aprobados_FA,
                                  film.prop_aprobados)

    def __set_cell_value(self, line: int, col: ExcelColumns, value, *, id=0):

        # Obtengo un objeto celda
        cell: Cell = self.ws.cell(row=line, column=col)
        # Le asigno el valor
        cell.value = value

        # Configuramos el estilo de la celda atendiendo a su columna
        # visionados. Ponemos punto de millar
        if (col == ExcelColumns.Visionados):
            cell.number_format = '#,##0'
        # booleano mayor que
        elif (col == ExcelColumns.Me_ha_gustado):
            cell.number_format = '0'
            cell.font = Font(name='SimSun', bold=True)
            cell.alignment = Alignment(horizontal='center', vertical='center')
        # Nota del usuario más el ruido
        elif (col == ExcelColumns.Mia_ruido):
            cell.number_format = '0.0'
        # Nota de FA más el ruido
        elif (col == ExcelColumns.FA or
              col == ExcelColumns.FA_ruido):
            cell.number_format = '0.00'
        # Varianza de los votos en FA
        elif (col == ExcelColumns.Varianza_FA):
            cell.number_format = '0.00'
        # Proporción de aprobados
        elif (col == ExcelColumns.Prop_aprobados_FA):
            cell.number_format = '0.00%'
        # reescala
        elif (col == ExcelColumns.Mia_rees or
              col == ExcelColumns.FA_rees or
              col == ExcelColumns.Diferencia or
              col == ExcelColumns.Diferencia_abs):
            cell.number_format = '0.00'
        # Nombre de la película con un hipervínculo
        elif (col == ExcelColumns.Id):
            # Añado un hipervínculo a su página
            cell.style = 'Hyperlink'
            cell.hyperlink = URL_FILM_ID(id)
            # Fuerzo el formato como texto
            cell.number_format = '@'
