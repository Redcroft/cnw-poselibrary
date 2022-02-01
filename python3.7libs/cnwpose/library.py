import hou
import psutil

from PySide2 import QtWidgets
from PySide2.QtGui import QMovie

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
        self.lbl_mem = QtWidgets.QLabel(
            f"{psutil.Process().memory_info().rss / (1024 * 1024)}")
        main_layout.addWidget(self.lbl_mem)
        self.grid_layout = QtWidgets.QGridLayout()
        self._refreshLibrary()
        self.setLayout(main_layout)
        main_layout.addLayout(self.grid_layout)

    def _refreshLibrary(self):
        filename = hou.expandString("$HOME/temp/clip.gif")
        self._clearLibrary()
        for x in range(3):
            for y in range(4):
                container = QtWidgets.QVBoxLayout()
                thumbnail = QtWidgets.QLabel()
                thumbnail.setMovie(QMovie(filename))
                thumbnail.movie().start()
                thumbnail.setScaledContents(True)
                thumbnail.setFixedSize(192, 192)
                label = QtWidgets.QLabel('Thumbnail')
                container.addWidget(thumbnail)
                container.addWidget(label)
                self.grid_layout.addLayout(container, x, y)

    def _clearLibrary(self):
        rows = self.grid_layout.rowCount()
        cols = self.grid_layout.columnCount()
        for i in range(rows*cols+1):
            container = self.grid_layout.itemAt(0)
            if container is not None:
                container.setParent(None)
                count = container.count()
                for i in range(count):
                    item = container.itemAt(i)
                    if item is not None:
                        widget = item.widget()
                        if widget is not None:
                            if widget.movie() is not None:
                                widget.movie().deleteLater()
                            if widget.pixmap() is not None:
                                widget.pixmap().deleteLater()
                            widget.setParent(None)
                            widget.deleteLater()
        self.lbl_mem.setText(
            f"{psutil.Process().memory_info().rss / (1024 * 1024):.2f} Mb memory used")
