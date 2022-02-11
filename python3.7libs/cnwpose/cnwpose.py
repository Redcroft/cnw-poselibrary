import hou
import json
import gzip
import sys
import time

from PySide2 import QtWidgets
from PySide2 import QtCore

from . import plglobals
from . import header
from . import capture
from . import library


'''
TODO: better name than cnwpose
'''

if plglobals.debug == 1:
    from importlib import reload
    reload(plglobals)
    reload(capture)
    reload(header)
    reload(library)


class CnwPose(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CnwPose, self).__init__()

    def buildGUI(self):
        '''
        Build the interface
        '''
        plglobals.debug = 1

        # Init modules
        self.header = header.UI()
        self.capture = capture.UI()
        self.library = library.UI()

        # Signals and slots
        self.header.path.connect(self.library.refreshLibrary)
        self.capture.capture.connect(self.library.refreshLibrary)

        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.capture, 'Capture')
        self.tab_widget.addTab(self.library, 'Library')
        self.tab_widget.setCurrentIndex(1)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.header)
        mainLayout.addWidget(self.tab_widget)
        self.setLayout(mainLayout)
