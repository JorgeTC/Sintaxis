from .progress_bar_base import ProgressBarBase


class ProgressBarDone(ProgressBarBase):
    def __init__(self):
        ProgressBarBase.__init__(self)
        self.calls = 0
        self._progress = 0.0

    def update(self, done: float):
        self._progress = done
        ProgressBarBase.update(self)

    @property
    def progress(self) -> float:
        return self._progress
