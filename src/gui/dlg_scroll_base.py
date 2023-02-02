import sys
from functools import wraps
from threading import Lock
from typing import Callable

import keyboard

from src.aux_console import is_console_on_focus
from src.gui.gui import ConsoleEvent


class DlgScrollBase(ConsoleEvent):

    keyboard_listen = Lock()

    def __init__(self, question: str = "", options: list[str] = None,
                 empty_option: bool = True, empty_ans: bool = False):
        ConsoleEvent.__init__(self)

        # Pregunta que voy a mostrar en pantalla
        self.sz_question = question
        # Opciones sobre las que hacer scroll
        self.sz_options = [] if options is None else options
        self.n_options = len(self.sz_options)

        # Si después del último elemento de la iteración se mostrará una string vacía
        self.SCROLL_EMPTY_OPTION = empty_option
        self.min_index = -1 if self.SCROLL_EMPTY_OPTION else 0

        # Si tolero una respuesta vacía
        self.ALLOW_EMPTY_ANS = empty_ans
        # Variable para guardar la respuesta
        self.sz_ans = ""

        # Índice que me dice cuál ha sido la última opción escrita
        self.curr_index = self.min_index

    def execute(self) -> str:
        # Doy a las flechas las funciones para hacer scroll
        keyboard.add_hotkey('up arrow', self.__scroll_up)
        keyboard.add_hotkey('down arrow', self.__scroll_down)

        ans = self.get_ans_body()

        # Cancelo la funcionalidad de las hotkeys
        keyboard.unhook_all()

        # Indico que ya he conseguido la respuesta
        self.locker.release()

        return ans

    def get_ans_body(self) -> str:
        self.sz_ans = ""
        # Función para sobrescribir.
        # Es la que hace la petición efectiva de un elemento de la lista
        while not self.sz_ans:
            # Inicializo las variables antes de llamar a input
            self.curr_index = self.min_index
            # Al llamar a input es cuando me espero que se utilicen las flechas
            self.sz_ans = input(self.sz_question)
            if not self.sz_ans and self.ALLOW_EMPTY_ANS:
                return self.sz_ans
            # Se ha introducido un título, compruebo que sea correcto
            self.sz_ans = self.sz_ans if self.sz_ans in self.sz_options else ''

        return self.sz_ans

    def hotkey_method(fn: Callable[['DlgScrollBase'], None]):
        @wraps(fn)
        def wrap(self: 'DlgScrollBase'):
            # Compruebo que la consola tenga el foco
            if not is_console_on_focus():
                return

            # Compruebo que no se esté ejecutando otra hotkey
            if self.keyboard_listen.locked():
                return

            # Inicio la ejecución de esta hotkey, evito que se ejecuten otras
            self.keyboard_listen.acquire()
            fn(self)
            # Ya he terminado la función, vuelvo a escuchar al teclado
            self.keyboard_listen.release()

        return wrap

    def __scroll(self, iter_fun: Callable[[int], int]):
        # si no tengo ninguna sugerencia, no puedo recorrer nada
        if not self.n_options:
            return

        clear_written()
        self.curr_index = iter_fun(self.curr_index)

        # Si el índice corresponde a un elemento de la lista, lo escribo
        if (self.curr_index != -1):
            curr_suggested = self.sz_options[self.curr_index]
            keyboard.write(curr_suggested)

    @hotkey_method
    def __scroll_up(self) -> None:
        self.__scroll(self.__prev_index)

    @hotkey_method
    def __scroll_down(self) -> None:
        self.__scroll(self.__next_index)

    def __next_index(self, current_index: int) -> int:
        # Compruebo si puedo aumentar mi posición en la lista
        if current_index < self.n_options - 1:
            # Puedo aumentar en la lista
            return current_index + 1
        else:
            # Doy la vuelta a la lista, empiezo por -1 si existe opción vacía
            # Empiezo por 0 si no existe opción vacía
            return self.min_index

    def __prev_index(self, current_index: int) -> int:
        # Compruebo si el índice es demasiado bajo (-1 o 0)
        if current_index <= self.min_index:
            # Le doy la última posición en la lista
            return self.n_options - 1
        else:
            # Puedo bajar una posición en la lista
            return current_index - 1

    def get_ans(self):
        ConsoleEvent.execute_if_main_thread(self)
        with self.locker:
            return self.sz_ans


def clear_written():
    # Al pulsar las teclas, también se está navegando entre los últimos inputs de teclado
    # Hago que se expliciten en la consola para poder borrarlos
    sys.stdout.flush()
    # Borro lo que haya escrito para que no lo detecte el input
    keyboard.send('esc')
