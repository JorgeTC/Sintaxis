import ast

from src.aux_res_directory import get_res_folder
from src.config import Config, Param, Section
from src.gui import DlgScrollBase


def load_users_id() -> dict[str, int]:
    sz_json = get_res_folder("Readdata", "usuarios.json")

    with open(sz_json, "r") as file:
        contents = file.read()
        dictionary = ast.literal_eval(contents)
    return dictionary


class Usuario:

    SZ_QUESTION = "Se van a importar los datos de {}\nEspero enter...".format
    DEFAULT_USER = Config.get_value(Section.READDATA, Param.DEFAULT_USER)
    IDS = load_users_id()

    def __init__(self, nombre: str = None, id: int = None):
        self.nombre: str = nombre
        self.id: int = id

    @classmethod
    def ask_user(cls) -> 'Usuario':

        instance = Usuario()

        asker = DlgScrollBase(question=cls.SZ_QUESTION(cls.DEFAULT_USER),
                              options=list(cls.IDS.keys()),
                              empty_ans=True)
        # Pido el nombre del usuario cuyos datos se quieren importar
        nombre = asker.get_ans()
        # Si no se ha introducido nada por teclado, utilizo el nombre default.
        if nombre:
            instance.nombre = nombre
        else:
            instance.nombre = cls.DEFAULT_USER

        # Sé que el diálogo me ha dado un usuario válido, estará en el diccionario
        instance.id = cls.IDS[instance.nombre]

        # Guardo la última elección del usuario en el ini
        Config.set_value(Section.READDATA, Param.DEFAULT_USER, instance.nombre)

        return instance
