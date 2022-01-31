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
    reload(library)


class CnwPose(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CnwPose, self).__init__()

    def buildGUI(self):
        '''
        Build the interface
        '''

        self.header = header.UI()
        self.capture = capture.UI()
        self.library = library.UI()

        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.capture, 'Capture')
        self.tab_widget.addTab(self.library, 'Library')

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
        print(f'time for loop: {time.time()-sec}')

        sec = time.time()
        jsn = json.dumps(anim_dict, indent=4)
        print(f'time to jsn: {time.time()-sec}')

        # GZip
        sec = time.time()
        cmp = gzip.compress(jsn.encode('UTF-8'))
        obj = gzip.decompress(cmp).decode('UTF-8')
        print(f'gzip time: {(time.time()-sec)*100:.4f}ms')

        # End
        print('Total Time: {(time.time()-tsec)*100:.4f}ms')
