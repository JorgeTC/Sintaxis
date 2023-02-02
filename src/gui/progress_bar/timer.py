from time import time


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
