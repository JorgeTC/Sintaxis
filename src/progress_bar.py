from time import time
import sys


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


class ProgressBar:
    def __init__(self):
        self.__timer = Timer()
        self.barLength = 20
        self.progress = 0.0

    def update(self, done):
        self.progress = float(done)
        block = int(round(self.barLength * self.progress))
        text = "[{0}] {1:.2f}% {2}\n".format( "="*block + " "*(self. barLength-block), self. progress*100, self.__timer.remains(self.progress))
        sys.stdout.write(text)
        sys.stdout.flush()

    def reset_timer(self):
        self.__timer.reset()
