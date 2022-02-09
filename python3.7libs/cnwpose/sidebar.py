import gzip
import hou
import json
import os
from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore
from . import plglobals
from . import utils

if plglobals.debug == 1:
    from importlib import reload
    reload(plglobals)
    reload(utils)


class UI(QtWidgets.QWidget):
    json_data = None
    scale_tog = 0

    def __init__(self, parent=None):
        super(UI, self).__init__()
        self.setStyleSheet(hou.qt.styleSheet())
        self.setStyleSheet('margin-left: 5px; margin-right: 5px;')
        self._createUI()

    def __del__(self):
        try:
            self.movie.setParent(None)
            del self.movie
        except AttributeError:
            pass

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

        # Form
        form_layout = QtWidgets.QFormLayout()

        # Info
        self.lbl_name = QtWidgets.QLabel()
        form_layout.addRow(QtWidgets.QLabel('Name'), self.lbl_name)
        self.lbl_type = QtWidgets.QLabel()
        form_layout.addRow(QtWidgets.QLabel('Type'), self.lbl_type)
        self.lbl_length = QtWidgets.QLabel()
        self.lbl_length_out = QtWidgets.QLabel()
        form_layout.addRow(QtWidgets.QLabel('Clip Length'), self.lbl_length)
        form_layout.addRow(QtWidgets.QLabel(
            'Output Length'), self.lbl_length_out)
        main_layout.addLayout(form_layout)

        # Settings
        self.scale = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.scale.setMinimum(0)
        self.scale.setMaximum(400)
        self.scale.setValue(100)
        self.scale.setSingleStep(25)
        self.scale.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.scale.setTickInterval(50)
        self.if_scale = hou.qt.InputField(hou.qt.InputField.FloatType, 1)
        self.scale.valueChanged.connect(self._scaleChanged)
        self.if_scale.valueChanged.connect(self._ifScaleChanged)
        self._scaleChanged()
        scale_layout = QtWidgets.QHBoxLayout()
        scale_layout.addWidget(self.if_scale)
        scale_layout.addWidget(self.scale)
        form_layout.addRow(QtWidgets.QLabel('Time Scale'), scale_layout)
        self.combo = QtWidgets.QComboBox()
        self.combo.addItem('Insert')
        self.combo.addItem('Merge')
        self.combo.addItem('Replace')
        self.combo.addItem('Replace All')
        form_layout.addRow(QtWidgets.QLabel('Insertion Method'), self.combo)
        # self.combo.setEnabled(False)
        self.btn_apply = QtWidgets.QPushButton('Apply')
        self.btn_apply.clicked.connect(self.applyJSON)
        form_layout.addRow(QtWidgets.QLabel(
            ''), self.btn_apply)
        # main_layout.addWidget(self.btn_apply)
        if plglobals.debug == 1:
            self.te_debug = QtWidgets.QPlainTextEdit()
            main_layout.addWidget(self.te_debug)

    def _clear(self):
        try:
            self.movie.stop()
            self.movie.setParent(None)
        except AttributeError:
            pass
        self.thumb.clear()
        self.lbl_name.setText('')
        self.lbl_type.setText('')
        self.lbl_length.setText('')
        self.lbl_length_out.setText('')
        self.scale.setValue(100)
        if plglobals.debug == 1:
            self.te_debug.setPlainText('')

    def _scaleChanged(self):
        if self.scale.value() > 85 and self.scale.value() < 115 and self.scale_tog == 1:
            self.scale.setValue(100)
            self.scale.setSliderPosition(100)
        self.if_scale.setValue(self.scale.value()/100.0)
        self._setOutLength()
        self.scale_tog = 1

    def _ifScaleChanged(self):
        self.scale_tog = 0
        if self.if_scale.value() < 0.0:
            self.if_scale.setValue(0.0)
        self.scale.setValue(self.if_scale.value()*100.0)
        self._setOutLength()

    def _setOutLength(self):
        mult = max(self.scale.value(), 1)
        val = hou.timeToFrame(self.getTimeLength() / (mult / 100.0))
        self.lbl_length_out.setText(str(val))
        try:
            self.movie.setSpeed(mult)
        except AttributeError:
            pass

    def updateClip(self):
        self.getJSON()
        self.setThumbnail()
        self.setInfo()
        self.scale.setValue(100)

    def getJSON(self):
        filename = os.path.join(plglobals.clip['dir'], plglobals.clip['name'])
        with gzip.open(filename, 'rt', encoding='UTF-8') as zipfile:
            self.json_data = json.load(zipfile)
        if plglobals.debug == 1:
            self.te_debug.setPlainText('')
            self.te_debug.insertPlainText(
                f"{plglobals.clip['name']}\n{plglobals.clip['dir']}\n{self.json_data}")

    def getTimeLength(self):
        end = 0.0
        if self.json_data != None:
            for parm in self.json_data:
                for k in self.json_data[parm]:
                    end = max(end, k['time'])
        return end

    def setInfo(self):
        self.lbl_name.setText(
            plglobals.clip['name'].capitalize().replace("_", " "))
        self.lbl_type.setText(plglobals.clip['type'].capitalize())
        self.lbl_length.setText(
            f"{hou.timeToFrame(self.getTimeLength())}")
        self._setOutLength()

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

    def _selectChannels(self):
        selection = hou.playbar.channelList().selected()
        if len(selection) == 0:
            selection = hou.playbar.channelList().parms()
        return selection

    def applyJSON(self):
        if self.json_data == None:
            utils.warningDialog("No Clip/Pose Data")
            return False
        sel = utils.selectChannels()
        if len(sel) == 0:
            utils.warningDialog("Nothing Selected")
            return False
        frame = hou.frame()
        time = hou.frameToTime(hou.frame())
        length = self.getTimeLength()
        mult = max(self.if_scale.value(), 0.01)
        length = hou.timeToFrame(length * mult)
        method = self.combo.currentText()
        jsn = self.json_data
        if method == "Insert":
            for c in sel:
                c_frames = c.keyframesAfter(frame)
                for k in c_frames:
                    c.deleteKeyframeAtFrame(k.frame())
                    k.setFrame(k.frame() + length)
                c.setKeyframes(c_frames)
        elif method == "Merge":
            # TODO: take keyframes and add the current value before applying
            # also remove all keyframes in place
            utils.warningDialog('Merge is not implemented yet')
            return False
        elif method == "Replace":
            # TODO: Remove all overlapping keyframes
            utils.warningDialog('Replace is not implemented yet')
            return False
        elif method == "Replace All":
            # TODO: Remove all keyframes first
            utils.warningDialog('Replace All is not implemented yet')
            return False
        for p, v in jsn.items():
            for c in sel:
                if c.name() == p:
                    for k in v:
                        frame = hou.Keyframe()
                        frame.fromJSON(k)
                        frame.setTime((frame.time() * mult) + time)
                        c.setKeyframe(frame)
