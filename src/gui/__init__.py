from threading import Thread

from src.gui.dlg_scroll_base import DlgScrollBase
from src.gui.gui import GUI
from src.gui.input import Input
from src.gui.log import Log
from src.gui.progress_bar import ProgressBar

consumer = Thread(target=GUI.run, daemon=True, name="GUI_Daemon")
consumer.start()


def join_GUI():
    GUI.add_event(None, None)
    consumer.join()


__all__ = [GUI, join_GUI, Log, Input, DlgScrollBase, ProgressBar]
