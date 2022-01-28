import hou

from PySide2 import QtWidgets
from PySide2 import QtCore

from . import plglobals


if plglobals.debug == 1:
    from importlib import reload
    reload(plglobals)


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

        help_text = QtWidgets.QLabel(globals.CAP_HELP_TEXT)
        help_text.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(help_text)

        self.le_cap_name = QtWidgets.QLineEdit()
        self.le_cap_name.setFixedWidth(hou.ui.scaledSize(300))
        self.le_cap_name.setMaxLength(38)
        form_layout = QtWidgets.QFormLayout()
        form_layout.setFormAlignment(QtCore.Qt.AlignHCenter)
        form_layout.addRow(QtWidgets.QLabel('Pose Name'), self.le_cap_name)
        main_layout.addLayout(form_layout)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def _channelListSelClip(self):
        '''
        Capture Animation clip from selected controls in the channel list.
        '''
        pass

    def _channelListSelPose(self):
        '''
        Capture a Pose from the selected controls in the channel list.
        '''
        pass

    def _channelListAllClip(self):
        '''
        Capture Animation clip from all controls in the channel list.
        '''
        pass

    def _channelListAllPose(self):
        '''
        Capture a Pose from all the control in the channel list.
        '''
        pass
