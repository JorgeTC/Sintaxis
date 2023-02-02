import enum
from configparser import ConfigParser
from functools import partial
from pathlib import Path

from src.aux_res_directory import get_res_folder

from .dlg_config import DlgConfig

SZ_FILE = "General.ini"


class Section(str, enum.Enum):
    HTML = "HTML"
    READDATA = "READDATA"
    COUNT_FILMS = "CONTAR"
    POST = "POST"
    DRIVE = "DRIVE"


class Param(str, enum.Enum):
    # Html
    FILTER_PUBLISHED = "Filter_published"
    SCRAP_BLOG = "Force_bog_scraping"
    ADD_STYLE = "Write_style"
    OUTPUT_PATH_HTML = "Path_output_html"
    YES_ALWAYS_DIR = "New_confidence_director"
    # Readdata
    FILTER_FA = "Filter_FilmAffinity"
    DEFAULT_USER = "Mem_user_FA"
    OUTPUT_EXCEL = "Path_output_excel"
    SAMPLE_OUTPUT = "Name_sample_output_file"
    PARALLELIZE = "Parallelize"
    # Count films
    ADD_YEAR = "Add_year"
    ADD_INDEX = "Add_index"
    WORD_FOLDER = "Folder_with_words"
    TITLE_LIST_PATH = "Output_folder_count"
    # Post
    BLOG_ID = "Blog_id"
    DATE = "Posting_date"
    TIME = "Posting_time"
    AS_DRAFT = "As_draft"
    FA_URL_FROM_HIDDEN_DATA = "Trust_FilmAffinity_url"
    GET_DATA_FROM_FA = "Download_film_data"
    # Drive
    FOLDER_ID = "Drive_folder_to_update_id"
    PDF_PATH = "Pdf_folder"


def add_default_value(config: ConfigParser, section: Section, param: Param, value) -> None:

    # Si no existe la sección, la añado
    if section not in config:
        config.add_section(section)
    # Si no existe el parámetro lo añado con el valor default
    if param not in config[section]:
        config.set(section, param, str(value))


class Config:

    # Abro el lector del archivo
    config = ConfigParser()
    # Dirección del ini
    sz_path = get_res_folder(SZ_FILE)
    config.read(sz_path, encoding="utf-8")

    add_def_value = partial(add_default_value, config)
    # Configuraciones para html
    add_def_value(Section.HTML, Param.FILTER_PUBLISHED, False)
    add_def_value(Section.HTML, Param.SCRAP_BLOG, False)
    add_def_value(Section.HTML, Param.ADD_STYLE, False)
    add_def_value(Section.HTML, Param.OUTPUT_PATH_HTML, 'auto')
    add_def_value(Section.HTML, Param.YES_ALWAYS_DIR, "")
    # Configuraciones para readdata
    add_def_value(Section.READDATA, Param.FILTER_FA, 1)
    add_def_value(Section.READDATA, Param.DEFAULT_USER, 'Jorge')
    add_def_value(Section.READDATA, Param.OUTPUT_EXCEL, 'auto')
    add_def_value(Section.READDATA, Param.SAMPLE_OUTPUT, 'Sample')
    add_def_value(Section.READDATA, Param.PARALLELIZE, True)
    # Configuraciones para escribir el txt
    add_def_value(Section.COUNT_FILMS, Param.ADD_YEAR, False)
    add_def_value(Section.COUNT_FILMS, Param.ADD_INDEX, False)
    add_def_value(Section.COUNT_FILMS, Param.WORD_FOLDER, 'auto')
    add_def_value(Section.COUNT_FILMS,
                  Param.TITLE_LIST_PATH, 'auto')
    # Configuraciones para post
    add_def_value(Section.POST, Param.BLOG_ID,
                  '4259058779347983900')
    add_def_value(Section.POST, Param.DATE, 'auto')
    add_def_value(Section.POST, Param.TIME, '20:00')
    add_def_value(Section.POST, Param.AS_DRAFT, False)
    add_def_value(Section.POST, Param.FA_URL_FROM_HIDDEN_DATA, True)
    add_def_value(Section.POST, Param.GET_DATA_FROM_FA, False)
    # Configuraciones para actualizar drive
    add_def_value(Section.DRIVE, Param.FOLDER_ID,
                  '13UbwzbjVFQ8e_UaNalqm_iMihjBDBvtm')
    add_def_value(Section.DRIVE, Param.PDF_PATH, 'auto')

    @classmethod
    def save_config(cls):
        with open(cls.sz_path, 'w', encoding="utf-8") as configfile:
            cls.config.write(configfile)

    @classmethod
    def get_value(cls, section: Section, param: Param) -> str:
        return cls.config[section][param]

    @classmethod
    def get_int(cls, section: Section, param: Param) -> int:
        return cls.config.getint(section, param)

    @classmethod
    def get_bool(cls, section: Section, param: Param) -> bool:
        return cls.config.getboolean(section, param)

    @classmethod
    def get_folder_path(cls, section: Section, param: Param) -> Path:
        # Leo lo que hya escrito en el ini
        ini_data = cls.config[section][param]

        # Compruebo que sea una carpeta
        while not Path(ini_data).is_dir():
            # Si no es una carpeta válida, la pido al usuario
            ini_data = input(
                f"Introducir path de la carpeta {section} {param}: ")
            # Guardo el dato elegido
            cls.set_value(section, param, ini_data)

        return Path(ini_data)

    @classmethod
    def get_file_path(cls, section: Section, param: Param) -> Path:
        # Leo lo que hya escrito en el ini
        ini_data = cls.config[section][param]

        # Compruebo que sea una carpeta
        while not Path(ini_data).is_file():
            # Si no es una carpeta válida, la pido al usuario
            ini_data = input(
                f"Introducir path del archivo {section} {param}: ")
            # Guardo el dato elegido
            cls.set_value(section, param, ini_data)

        return Path(ini_data)

    @classmethod
    def set_value(cls, section: Section, param: Param, value) -> None:
        # Me espero que se introduzca un valor en una sección que existe
        if param not in cls.config[section]:
            assert (f"{param} no pertenece a la sección {section}.")

        # Lo cambio en el objeto
        cls.config.set(section, param, str(value))

        # Actualizo el archivo ini
        cls.save_config()

    @classmethod
    def run_dlg(cls):
        dlg_config = DlgConfig(cls.config)
        dlg_config.run()


def manage_config():
    # Importo los módulos de windows para comprobar el teclado
    import win32api
    import win32con

    # Comrpuebo si la tecla control está apretada
    if win32api.GetAsyncKeyState(win32con.VK_CONTROL) & 0x8000 > 0:
        # Abro el diálogo
        Config.run_dlg()
        Config.save_config()
