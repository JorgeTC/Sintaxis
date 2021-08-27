from pathlib import Path
import ast

class Usuario(object):
    def __init__(self):
        self.ids = self.read_dict()
        self.nombre = "Jorge"
        self.id = 0

        self.ask_user()

    def read_dict(self):

        sz_curr_folder = Path(__file__).resolve().parent
        sz_curr_folder = sz_curr_folder / "Readdata"
        sz_json = sz_curr_folder / "usuarios.json"

        file = open(sz_json, "r")
        contents = file.read()
        dictionary = ast.literal_eval(contents)

        file.close()

        return dictionary

    def ask_user(self):
        while True:
            # Informamos de qué usuario está cargado
            print("Se van a importar los datos de ", self.nombre)
            inp = input("Espero Enter...")

            # No se ha introducido nada por teclado
            if not inp:
                break

            # Se ha introducido un nombre incorrecto.
            # Doy una nueva oportunidad para que introduzca otro nombre
            if not (inp in self.ids.keys()):
                continue
            # Si se ha introducido un nombre válido lo guardo como el usuario
            self.nombre = inp
            print("Se van a importar los datos de ", self.nombre)
            break

        # Sólo hemos salido del bucle si el id es válido
        self.id = self.ids[self.nombre]
