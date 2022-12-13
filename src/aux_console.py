import win32gui as wg

# Memorizo la dirección de la consola
CURRENT_CONSOLE = wg.GetForegroundWindow()


def is_console_on_focus() -> bool:
    # Devuelvo si la ventana en foco actual es la consola
    return wg.GetForegroundWindow() == CURRENT_CONSOLE

