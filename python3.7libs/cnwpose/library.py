import hou
import psutil

from PySide2 import QtWidgets
from PySide2.QtGui import QPixmap

from . import plglobals

if plglobals.debug == 1:
    from importlib import reload
    reload(plglobals)


class UI(QtWidgets.QWidget):
    """ Contains all the widgets to create the library interface."""

    def __init__(self, parent=None):
        super(UI, self).__init__()
        self.setStyleSheet("magin:5px;")
        self._createUI()

    def _createUI(self):
        """ Build the UI """
        main_layout = QtWidgets.QVBoxLayout()
        self.btn_refresh = QtWidgets.QPushButton('Refresh')
        self.btn_refresh.clicked.connect(self._refreshLibrary)
        main_layout.addWidget(self.btn_refresh)
        self.btn_clear = QtWidgets.QPushButton('Clear')
        self.btn_clear.clicked.connect(self._clearLibrary)
        main_layout.addWidget(self.btn_clear)
        self.lbl_mem = QtWidgets.QLabel(f"{psutil.Process().memory_info().rss / (1024 * 1024)}")
        main_layout.addWidget(self.lbl_mem)
        self.grid_layout = QtWidgets.QGridLayout()
        self._refreshLibrary()
        self.setLayout(main_layout)
        main_layout.addLayout(self.grid_layout)

    def _refreshLibrary(self):
        filename = hou.expandString("$HOME/screenshot.jpg")
        self._clearLibrary()
        for x in range(3):
            for y in range(3):
                label = QtWidgets.QLabel(f"{x}, {y}")
                label.setPixmap(QPixmap(filename).scaled(192, 192))
                self.grid_layout.addWidget(label,x,y)
        self.lbl_mem.setText(f"{psutil.Process().memory_info().rss / (1024 * 1024)}")

    def _clearLibrary(self):
        rows = self.grid_layout.rowCount()
        cols = self.grid_layout.columnCount()
        for i in range(10):
            item = self.grid_layout.itemAt(0)
            print(f"i = {i}\t{item}")
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    self.grid_layout.removeWidget(widget)
                    widget.deleteLater()
        self.lbl_mem.setText(f"{psutil.Process().memory_info().rss / (1024 * 1024)}")
