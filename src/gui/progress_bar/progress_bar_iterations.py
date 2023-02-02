from .progress_bar_base import ProgressBarBase


class ProgressBarIterations(ProgressBarBase):
    def __init__(self, iterations: int):
        ProgressBarBase.__init__(self)
        self.calls = 0
        self.iterations = iterations

    @property
    def progress(self) -> float:
        return float(self.calls) / float(self.iterations)

    def update(self):
        self.calls += 1
        ProgressBarBase.update(self)
