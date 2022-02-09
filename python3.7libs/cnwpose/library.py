import collections
import hou
import os
import psutil

from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2.QtGui import QMovie

from . import plglobals
from . import sidebar
from . import widgets

if plglobals.debug == 1:
    from importlib import reload
    reload(plglobals)
    reload(sidebar)
    reload(widgets)


class UI(QtWidgets.QWidget):
    """ Contains all the widgets to create the library interface."""

    def __init__(self, parent=None):
        super(UI, self).__init__()
        self.setStyleSheet("magin:5px;")
        self._createUI()

    def __del__(self):
        self._clearLibrary()

    def _createUI(self):
        """ Build the UI """
        main_layout = QtWidgets.QHBoxLayout()
        lib_widget = QtWidgets.QWidget()
        lib_layout = QtWidgets.QVBoxLayout(lib_widget)
        main_layout.addLayout(lib_layout)

        # Splitter
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        main_layout.addWidget(splitter)
        splitter.addWidget(lib_widget)
        self.sidebar = sidebar.UI()
        splitter.addWidget(self.sidebar)

        splitter.setSizes([hou.ui.scaledSize(400),
                           hou.ui.scaledSize(10)])

        # Library Side
        if plglobals.debug == 1:
            self.lbl_mem = QtWidgets.QLabel()
            self.lbl_mem.setText(
                f"{psutil.Process().memory_info().rss / (1024 * 1024):.2f} Mb memory used")
            lib_layout.addWidget(self.lbl_mem)
        btn_layout = QtWidgets.QHBoxLayout()
        lib_layout.addLayout(btn_layout)
        self.btn_r = QtWidgets.QPushButton('Reload')
        self.btn_r.clicked.connect(self.refreshLibrary)
        btn_layout.addWidget(self.btn_r)
        self.btn = QtWidgets.QPushButton('Clear')
        self.btn.clicked.connect(self._clearLibrary)
        btn_layout.addWidget(self.btn)

        # Thumbnails
        self.flow = widgets.ScrollingFlowWidget()
        lib_layout.addWidget(self.flow)

        # Zoom widget
        self.zoom = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.zoom.setMinimum(hou.ui.scaledSize(64))
        self.zoom.setMaximum(hou.ui.scaledSize(384))
        self.zoom.setValue(hou.ui.scaledSize(128))
        self.zoom.valueChanged.connect(self._resizeBtns)
        lib_layout.addWidget(self.zoom)

        self.refreshLibrary()
        self.setLayout(main_layout)

    def refreshLibrary(self):
        self._clearLibrary()
        try:
            lib_dir = plglobals.lib_path
            clips = []
            for f in ('clip', 'pose'):
                sub_dir = os.path.join(lib_dir, f)
                if os.path.isdir(sub_dir):
                    for i in os.listdir(sub_dir):
                        clip_dir = os.path.join(sub_dir, i)
                        if os.path.isdir(clip_dir):
                            dict = {"name": i,
                                    "dir": clip_dir,
                                    "type": f}
                            clips.append(dict)
                            clips = sorted(
                                clips, key=lambda c: c['name'].lower())
            for i in clips:
                clip = widgets.QImageThumbnail()
                clip.setText(i['name'])
                clip.setPath(i['dir'])
                clip.setType(i['type'])
                self.flow.addWidget(clip)
                clip.clicked.connect(self.getClip)
                gif = os.path.join(i['dir'], i['name'] + '.gif')
                jpg = os.path.join(i['dir'], i['name'] + '.jpg')
                if os.path.isfile(gif):
                    clip.setMovie(gif)
                elif os.path.isfile(jpg):
                    clip.setImage(jpg)
                    self._resizeBtns()
        except Exception as e:
            print(e)

    def getClip(self):
        self.sidebar.updateClip()

    def _resizeBtns(self):
        count = self.flow.count()
        for i in range(count):
            item = self.flow.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.setFixedSize(self.zoom.value(),
                                        self.zoom.value()+26)

    def _clearLibrary(self):
        self.sidebar._clear()
        count = self.flow.count()
        for i in range(count):
            item = self.flow.itemAt(0)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                    del widget
        if plglobals.debug == 1:
            self.lbl_mem.setText(
                f"{psutil.Process().memory_info().rss / (1024 * 1024):.2f} Mb memory used")
