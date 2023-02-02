import sys

from src.gui.gui import ConsoleEvent

from .timer import Timer


class ProgressBarBase(ConsoleEvent):
    def __init__(self):
        ConsoleEvent.__init__(self)
        self.__timer = Timer()
        self.barLength = 20

    @property
    def progress(self) -> float:
        raise NotImplementedError

    def execute(self):
        block = int(round(self.barLength * self.progress))
        text = "[{0}] {1:.2f}% {2}\n".format(
            "=" * block + " " * (self.barLength - block),
            self.progress * 100,
            self.__timer.remains(self.progress))
        sys.stdout.write(text)

    def update(self):
        ConsoleEvent.execute_if_main_thread(self)

    def reset_timer(self):
        self.__timer.reset()
