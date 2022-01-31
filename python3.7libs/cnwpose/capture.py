import gzip
import hou
import json
import os

from PySide2 import QtWidgets
from PySide2 import QtCore

from . import plglobals
from . import utils


if plglobals.debug == 1:
    from importlib import reload
    reload(plglobals)
    reload(utils)


class UI(QtWidgets.QWidget):
    """ Contains all the widgets to create a capture interface."""

    def __init__(self, parent=None):
        super(UI, self).__init__()
        self.setStyleSheet("margin:5px;")
        self._createUI()

    def _createUI(self):
        '''
        Build the ui
        '''
        main_layout = QtWidgets.QVBoxLayout()

        help_text = QtWidgets.QLabel(plglobals.CAP_HELP_TEXT)
        help_text.setAlignment(QtCore.Qt.AlignCenter)
        help_text.setWordWrap(True)
        main_layout.addWidget(help_text)

        # Pose Name fields
        self.le_cap_name = QtWidgets.QLineEdit()
        self.le_cap_name.setFixedWidth(hou.ui.scaledSize(300))
        self.le_cap_name.setMaxLength(38)
        self.le_cap_name.setText('Default')
        form_layout = QtWidgets.QFormLayout()
        form_layout.setFormAlignment(QtCore.Qt.AlignHCenter)
        form_layout.addRow(QtWidgets.QLabel('Capture Name'), self.le_cap_name)
        main_layout.addLayout(form_layout)

        # Capture Buttons
        self.btn_cap_clip = QtWidgets.QPushButton('Capture Clip')
        self.btn_cap_clip.setFixedWidth(hou.ui.scaledSize(147))
        self.btn_cap_clip.clicked.connect(self._captureClip)
        self.btn_cap_pose = QtWidgets.QPushButton('Capture Pose')
        self.btn_cap_pose.clicked.connect(self._capturePose)
        self.btn_cap_pose.setFixedWidth(hou.ui.scaledSize(147))
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.btn_cap_clip)
        btn_layout.addWidget(self.btn_cap_pose)
        form_layout.addRow(QtWidgets.QLabel(), btn_layout)

        # Debug
        self.te_debug = QtWidgets.QPlainTextEdit()
        main_layout.addWidget(self.te_debug)
        # main_layout.addStretch()
        self.setLayout(main_layout)

    def _captureClip(self):
        '''Capture Animation clip from the selected channels.
The time range is offset to start at frame 0, rather than when it currently starts'''
        frame_range = hou.playbar.selectionRange()
        if frame_range == None:
            frame_range = hou.playbar.frameRange()
        start_time = hou.frameToTime(frame_range[0])
        sel_channels = self._selectChannels()
        anim_dict = {}
        for p in sel_channels:
            key_frames = p.keyframesInRange(frame_range[0], frame_range[1])
            if key_frames:
                key_frames_list = []
                for f in key_frames:
                    frame = f.asJSON()
                    frame['time'] = frame['time'] - start_time
                    key_frames_list.append(frame)
                    anim_dict[str(p.name())] = key_frames_list
            else:
                anim_dict[str(p.name())] = self._jsonFromValue(
                    hou.frameToTime(frame_range[0])-start_time, p.eval())
        jsn = json.dumps(anim_dict, indent=4)
        self.te_debug.clear()
        filename = os.path.join(hou.expandString(plglobals.lib_path),
                                "clips",
                                self.le_cap_name.text().replace(" ", "_"))
        self.te_debug.insertPlainText(
            f"Storing Clip\nFrame Range: {frame_range[0]} {frame_range[1]}\n")
        self.te_debug.insertPlainText(
            f"Output Range: {frame_range[0] - frame_range[0]} {frame_range[1] - frame_range[0]}\n")
        self.te_debug.insertPlainText(f"Sel Node: {sel_channels[0].node()}\n")
        self.te_debug.insertPlainText(f"Filename: '{filename}.'\n\n")
        self.te_debug.insertPlainText("File Contents:\n")
        self.te_debug.insertPlainText(str(jsn))

    def _capturePose(self):
        '''Capture a Pose from the selected controls in the channel list. The stored frame starts from zero'''
        sel_channels = self._selectChannels()
        anim_dict = {}
        for p in sel_channels:
            anim_dict[str(p.name())] = self._jsonFromValue(
                0.0, p.eval())
        print(anim_dict)
        jsn = json.dumps(anim_dict, indent=4)
        self.te_debug.clear()
        filename = os.path.join(hou.expandString(plglobals.lib_path),
                                "clips",
                                self.le_cap_name.text().replace(" ", "_"))
        self.te_debug.insertPlainText(
            f"Storing Pose\nFrame: {hou.frame()}\n")
        self.te_debug.insertPlainText(f"Sel Node: {sel_channels[0].node()}\n")
        self.te_debug.insertPlainText(f"Filename: '{filename}.'\n\n")
        self.te_debug.insertPlainText("File Contents:\n")
        self.te_debug.insertPlainText(str(jsn))

    def _selectChannels(self):
        ''' Return a tuple of all the currently selected channels in the
        Channel List'''
        selection = hou.playbar.channelList().selected()
        return selection

    def _jsonFromValue(self, time, value):
        return [{'time': time, 'value': value, 'slope': 0.0,
                 'inSlope': 0.0, 'accel': 0.0, 'accelRatio': 0,
                 'expression': 'bezier()', 'language': 'Hscript'}]

    def _writeToFile(self, data, filename):
        dir = os.path.dirname(filename)
        if not os.path.exists(dir):
            os.mkdirs(dir)
        try:
            with gzip.open(filename, 'wt', encoding='UTF-8') as zipfile:
                json.dump(data, zipfile)
        except IOError as e:
            utils.warningDialog(f"Unable to write file.\nError: {e}")

    def _readFromFile(self, filename):
        try:
            with gzip.open(filename, 'rt', encoding='UTF-8') as zipfile:
                return json.load(zipfile)
        except IOError as e:
            utils.warningDialog(f"Unable to read file.\nError: {e}")
            return False
