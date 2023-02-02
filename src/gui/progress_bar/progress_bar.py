from .progress_bar_done import ProgressBarDone
from .progress_bar_iterations import ProgressBarIterations


# Interfaz para barra de progreso.
# Si introduzco la cantidad de iteraciones avanzará lo correspondiente con cada `update`.
# De lo contrario hay que introducir la proporción de progreso completado.
class ProgressBar:
    def __new__(self, iterations: int = None):
        if iterations is not None:
            return ProgressBarIterations(iterations)
        else:
            return ProgressBarDone()
