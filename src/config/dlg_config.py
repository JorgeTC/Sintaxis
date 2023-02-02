from functools import partial

from configparser import ConfigParser

from src.gui import DlgScrollBase

SZ_SECTIONS = "Secciones: "
SZ_PARAMETROS = "Parámetros: "
SZ_NEW_VALUE = "Nuevo valor de {}: ".format

SZ_WELCOME = "## BIENVENIDO A LA CONFIGURACIÓN ##"
SZ_CLOSE = "### SALIENDO DE LA CONFIGURACIÓN ##"
SZ_PRINT_VALUE = "  {}: {}".format


class DlgConfig:

    def __init__(self, config: ConfigParser):

        self.config = config

    def run(self):
        print(SZ_WELCOME)
        self.print()
        self.__choose_section()
        print(SZ_CLOSE)

    def __choose_section(self):
        new_dlg = partial(DlgScrollBase, SZ_SECTIONS,
                          self.config.sections(), empty_ans=True)
        # Me muevo hasta la sección que sea menester
        while (current_section := new_dlg().get_ans()):
            self.__choose_param(current_section)

    def __choose_param(self, section: str):
        # Me muevo hasta la sección que sea menester
        params = [name for name, val in self.config.items(section)]
        new_dlg = partial(DlgScrollBase, SZ_PARAMETROS, params, empty_ans=True)
        while (current_param := new_dlg().get_ans()):
            self.__ask_param_value(section, current_param)
            self.print_section(section)

    def __ask_param_value(self, section: str, param: str):
        ans = input(SZ_NEW_VALUE(param))
        self.config.set(section, param, ans)

    def print(self):
        for section in self.config.sections():
            self.print_section(section)

    def print_section(self, section: str):
        print(section.upper())
        for param in self.config[section]:
            print(SZ_PRINT_VALUE(param, self.config[section][param]))
