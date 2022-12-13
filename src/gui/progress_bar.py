from time import time
import sys

from src.gui.gui import ConsoleEvent


class Timer:
    def __init__(self):
        self.start = time()

    def remains(self, done: float) -> str:
        if done == 0:
            return
        now = time()
        left = (1 - done) * (now - self.start) / done
        sec = int(left)
        if sec < 60:
            return f"{sec} seconds"
        else:
            return f"{int(sec / 60)} minutes"

    def reset(self) -> None:
        self.start = time()


class ProgressBar(ConsoleEvent):
    def __init__(self, iterations: int):
        ConsoleEvent.__init__(self)
        self.__timer = Timer()
        self.barLength = 20
        self.calls = 0
        self.iterations = iterations

    @property
    def progress(self) -> float:
        return float(self.calls) / float(self.iterations)

    def execute(self):
        self.calls += 1
        block = int(round(self.barLength * self.progress))
        text = "[{0}] {1:.2f}% {2}\n".format(
            "=" * block + " " * (self. barLength-block),
            self.progress * 100,
            self.__timer.remains(self.progress))
        sys.stdout.write(text)
        sys.stdout.flush()

    def update(self):
        ConsoleEvent.execute_if_main_thread(self)

    def reset_timer(self):
        self.__timer.reset()
