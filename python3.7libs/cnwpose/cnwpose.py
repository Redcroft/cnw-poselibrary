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


'''
TODO: better name than cnwpose
TODO: create capture UI
TODO: create view UI
TODO: capture flipbook stills/images
TODO: frame insertion methods
TODO: benchmark uncompressed vs gzip vs bz2 on final setup
TODO: look into PySide2.QtGui.QMovie
TODO: add easter egg
'''

if plglobals.debug == 1:
    from importlib import reload
    reload(plglobals)
    reload(capture)
    reload(header)


class CnwPose(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CnwPose, self).__init__()

    def buildGUI(self):
        '''
        Build the interface
        '''

        self.header = header.UI()
        self.capture = capture.UI()

        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.capture, 'Capture')
        wip = QtWidgets.QLabel('TODO')
        wip.setAlignment(QtCore.Qt.AlignCenter)
        self.tab_widget.addTab(wip, 'Library')

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.header)
        mainLayout.addWidget(self.tab_widget)
        self.setLayout(mainLayout)

    def getSelChannels(self):
        print('------')
        tsec = time.time()
        sel = hou.playbar.channelList().selected()
        anim_dict = {}
        sec = time.time()
        for i in sel:
            key_frames = i.keyframes()
            if key_frames:
                key_frames_list = []
                for f in key_frames:
                    frame = f.asJSON()
                    key_frames_list.append(frame)
                    anim_dict[str(i.name())] = key_frames_list
        print('time for loop: {}'.format(time.time()-sec))

        sec = time.time()
        jsn = json.dumps(anim_dict, indent=4)
        print('time to jsn: {}'.format(time.time()-sec))

        # GZip
        sec = time.time()
        cmp = gzip.compress(jsn.encode('UTF-8'))
        obj = gzip.decompress(cmp).decode('UTF-8')
        print('gzip time: {0:.4f}ms'.format((time.time()-sec)*100))

        # End
        print('Total Time: {0:.4f}ms'.format((time.time()-tsec)*100))
