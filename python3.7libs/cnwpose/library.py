import hou
import os
import psutil

from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2.QtGui import QMovie

from . import plglobals
from . import widgets

if plglobals.debug == 1:
    from importlib import reload
    reload(plglobals)
    reload(widgets)


class UI(QtWidgets.QWidget):
    """ Contains all the widgets to create the library interface."""

    def __init__(self, parent=None):
        super(UI, self).__init__()
        self.setStyleSheet("magin:5px;")
        self._createUI()

    def _createUI(self):
        """ Build the UI """
        # self.btn_refresh = QtWidgets.QPushButton('Refresh')
        # self.btn_refresh.clicked.connect(self._refreshLibrary)
        # main_layout.addWidget(self.btn_refresh)
        # self.btn_clear = QtWidgets.QPushButton('Clear')
        # self.btn_clear.clicked.connect(self._clearLibrary)
        # main_layout.addWidget(self.btn_clear)
        # self.lbl_mem = QtWidgets.QLabel(
        #     f"{psutil.Process().memory_info().rss / (1024 * 1024)}")
        # main_layout.addWidget(self.lbl_mem)
        # self.grid_layout = QtWidgets.QGridLayout()
        # self._refreshLibrary()
        main_layout = QtWidgets.QVBoxLayout()

        for i in range(10):
            main_layout.addWidget(widgets.QImageThumbnail())

        self.setLayout(main_layout)

    def _refreshLibrary(self):
        dir = hou.expandString(plglobals.lib_path)
        cols, x, y = 3, 0, 0
        clips = os.path.join(dir, "clips")
        items = os.listdir(clips)
        self._clearLibrary()
        for i in items:
            filename = os.path.join(clips, i, i)
            if os.path.exists(filename):
                container = QtWidgets.QVBoxLayout()
                thumbnail = QtWidgets.QLabel()
                thumbnail.setMovie(QMovie("{}.gif".format(filename)))
                thumbnail.movie().start()
                thumbnail.setScaledContents(True)
                thumbnail.setFixedSize(192, 192)
                label = QtWidgets.QLabel(i)
                label.setFixedWidth(192)
                label.setAlignment(QtCore.Qt.AlignCenter)
                container.addWidget(thumbnail)
                container.addWidget(label)
                self.grid_layout.addLayout(container, x, y)
                y += 1
                if y > cols:
                    x += 1
                    y = 0

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
