from src.gui.gui import ConsoleEvent

def Log(message: str):
    CLog(message)

class CLog(ConsoleEvent):
    def __init__(self, message: str) -> None:
        ConsoleEvent.__init__(self)

        self.message = message

        ConsoleEvent.execute_if_main_thread(self)

    def execute(self) -> None:
        print(self.message)
