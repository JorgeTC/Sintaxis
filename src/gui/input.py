from src.gui.gui import ConsoleEvent


def Input(message: str) -> str:
    input_dlg = CInput(message)
    return input_dlg.get_ans()


class CInput(ConsoleEvent):
    def __init__(self, message: str) -> None:
        ConsoleEvent.__init__(self)

        # Mensaje que imprimo para pedir información
        self.message = message
        # Respuesta escrita por el usuario
        self.ans: str = None

        ConsoleEvent.execute_if_main_thread(self)

    def execute(self):
        self.ans = input(self.message)
        self.locker.release()

    def get_ans(self) -> str:
        # Hasta que no se libere el locker, no tendré disponible la respuesta
        with self.locker:
            return self.ans
