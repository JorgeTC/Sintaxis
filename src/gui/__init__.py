from threading import Thread

from src.gui.dlg_bool import YesNo
from src.gui.dlg_scroll_base import DlgScrollBase
from src.gui.gui import GUI
from src.gui.input import Input
from src.gui.log import Log
from src.gui.progress_bar import ProgressBar

consumer = Thread(target=GUI.run, daemon=True, name="GUI_Daemon")
consumer.start()


def join_GUI():
    GUI.close_gui()
    consumer.join()


__all__ = [GUI, join_GUI, Log, Input, DlgScrollBase, ProgressBar, YesNo]
