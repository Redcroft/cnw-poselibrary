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
        form_layout.addRow(QtWidgets.QLabel('Pose Name'), self.le_cap_name)
        main_layout.addLayout(form_layout)

        # Capture Buttons
        self.btn_cap_clip = QtWidgets.QPushButton('Capture Clip')
        self.btn_cap_clip.setFixedWidth(hou.ui.scaledSize(147))
        self.btn_cap_clip.clicked.connect(self._captureClip)
        self.btn_cap_pose = QtWidgets.QPushButton('Capture Pose')
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
        '''Capture Animation clip from the selected channels'''
        frame_range = hou.playbar.selectionRange()
        if frame_range == None:
            utils.warningDialog(
                'Please select a valid Frame Range in the Timeline')
            pass
        sel_channels = self._selectChannels()
        anim_dict = {}
        for p in sel_channels:
            key_frames = p.keyframesInRange(frame_range[0], frame_range[1])
            if key_frames:
                key_frames_list = []
                for f in key_frames:
                    frame = f.asJSON()
                    key_frames_list.append(frame)
                    anim_dict[str(p.name())] = key_frames_list
            else:
                anim_dict[str(p.name())] = [{
                    'time': frame_range[0], 'value': p.eval(),
                    'slope': 0.0, 'inSlope': 0.0, 'accel': 0.0,
                    'accelRatio': 0, 'expression': 'bezier()',
                    'language': 'Hscript'}, ]
        jsn = json.dumps(anim_dict, indent=4)
        self.te_debug.clear()
        filename = os.path.join(hou.expandString(
            plglobals.lib_path), "clips", self.le_cap_name.text())
        self.te_debug.insertPlainText("Filename: '{}'\n\n".format(filename))
        self.te_debug.insertPlainText("File Contents:\n")
        self.te_debug.insertPlainText(str(jsn))

    def _capturePose(self):
        '''Capture a Pose from the selected controls in the channel list'''
        pass

    def _selectChannels(self):
        ''' Return a tuple of all the currently selected channels in the
        Channel List'''
        selection = hou.playbar.channelList().selected()
        return selection
