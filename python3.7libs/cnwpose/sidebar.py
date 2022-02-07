import gzip
import hou
import json
import os
import sys
from PySide2 import QtWidgets
from PySide2 import QtGui
from . import plglobals

if plglobals.debug == 1:
    from importlib import reload
    reload(plglobals)


class UI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(UI, self).__init__()
        self.setStyleSheet(hou.qt.styleSheet())
        self.setStyleSheet('margin-left: 5px; margin-right: 5px;')
        self._createUI()

    def __del__(self):
        self.movie.setParent(None)
        del self.movie

    def _createUI(self):
        '''
        Build the ui
        '''
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)
        spacer = QtWidgets.QSpacerItem(0, 12, QtWidgets.QSizePolicy.Expanding)

        # Thumbnail
        thumb_layout = QtWidgets.QHBoxLayout()
        thumb_layout.addStretch()
        self.thumb = QtWidgets.QLabel()
        self.thumb.setFixedSize(hou.ui.scaledSize(164), hou.ui.scaledSize(164))
        self.thumb.setScaledContents(True)
        self.thumb.setParent(self)

        thumb_layout.addWidget(self.thumb)
        thumb_layout.addStretch()
        main_layout.addSpacerItem(spacer)
        main_layout.addLayout(thumb_layout)
        main_layout.addSpacerItem(spacer)

        # Info
        info_layout = QtWidgets.QFormLayout()
        self.lbl_name = QtWidgets.QLabel()
        info_layout.addRow(QtWidgets.QLabel('Name'), self.lbl_name)
        self.lbl_type = QtWidgets.QLabel()
        info_layout.addRow(QtWidgets.QLabel('Type'), self.lbl_type)
        self.lbl_range = QtWidgets.QLabel()
        info_layout.addRow(QtWidgets.QLabel('Frame Range'), self.lbl_range)
        main_layout.addLayout(info_layout)

        # Settings
        self.combo = QtWidgets.QComboBox()
        self.combo.addItem('Insert')
        self.combo.addItem('Merge')
        self.combo.addItem('Replace')
        self.combo.addItem('Replace All')
        main_layout.addWidget(self.combo)
        self.combo.setEnabled(False)
        self.btn_apply = QtWidgets.QPushButton('Apply')
        main_layout.addWidget(self.btn_apply)
        if plglobals.debug == 1:
            self.te_debug = QtWidgets.QPlainTextEdit()
            main_layout.addWidget(self.te_debug)

    def updateClip(self):
        self.getJSON()
        self.setThumbnail()
        self.setInfo()

    def getJSON(self):
        filename = os.path.join(plglobals.clip['dir'], plglobals.clip['name'])
        with gzip.open(filename, 'rt', encoding='UTF-8') as zipfile:
            data = json.load(zipfile)
        self.getFrameRange(data)
        if plglobals.debug == 1:
            self.te_debug.setPlainText('')
            self.te_debug.insertPlainText(
                f"{plglobals.clip['name']}\n{plglobals.clip['dir']}\n{data}")

    def getFrameRange(self, data):
        print(data)

    def setInfo(self):
        self.lbl_name.setText(
            plglobals.clip['name'].capitalize().replace("_", " "))
        self.lbl_type.setText(plglobals.clip['type'].capitalize())

    def setThumbnail(self):
        self.thumb.clear()
        gif = os.path.join(
            plglobals.clip['dir'], plglobals.clip['name'] + '.gif')
        jpg = os.path.join(
            plglobals.clip['dir'], plglobals.clip['name'] + '.jpg')
        if os.path.isfile(gif):
            self.movie = QtGui.QMovie(gif)
            self.thumb.setMovie(self.movie)
            self.movie.start()
        elif os.path.isfile(jpg):
            self.pixmap = QtGui.QPixmap(jpg)
            self.thumb.setPixmap(self.pixmap)
