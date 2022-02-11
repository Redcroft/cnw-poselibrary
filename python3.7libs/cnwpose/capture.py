import gzip
import hou
import json
import os
import re
import shutil

from PIL import Image
from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui

from . import plglobals
from . import thumb
from . import utils


if plglobals.debug == 1:
    from importlib import reload
    reload(thumb)
    reload(plglobals)
    reload(utils)


class UI(QtWidgets.QWidget):
    """ Contains all the widgets to create a capture interface."""
    capture = QtCore.Signal()
    cancel = False

    def __init__(self, parent=None):
        super(UI, self).__init__()
        self.setStyleSheet("margin:5px;")
        self._createUI()

    def _createUI(self):
        '''
        Build the ui
        '''
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

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
        if plglobals.debug == 1:
            main_layout.addWidget(self.te_debug)

        main_layout.addStretch()

    def _captureClip(self):
        '''Capture Animation clip from the selected channels.
The time range is offset to start at frame 0, rather than when it currently starts'''
        frame_range = hou.playbar.selectionRange()
        if frame_range == None:
            frame_range = hou.playbar.frameRange()
        if frame_range[0] < 1:
            frame_range[0] = 1
        start_time = hou.frameToTime(frame_range[0])
        sel_channels = utils.selectChannels()
        if len(sel_channels) == 0:
            utils.warningDialog(
                'No channels are available in the Channel List')
            return False
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
        clip_name = re.sub(r'\W+', '_', self.le_cap_name.text())
        dir = os.path.join(hou.expandString(
            plglobals.lib_path), "clip", clip_name)
        object = sel_channels[0].node()
        while(type(object) is not hou.ObjNode):
            object = object.parent()
        if clip_name == 'gary':
            thumb.placeholder(os.path.join(dir, clip_name + '.jpg'))
            utils.warningDialog('Why would you name it that?...')
        else:
            ok = self._captureThumbnailSequence(
                frame_range, object, clip_name, dir)
            if not ok:
                return False
        self._writeToFile(anim_dict, clip_name, dir)
        self.capture.emit()

    def _capturePose(self):
        '''Capture a Pose from the selected controls in the channel list. The stored frame starts from zero'''
        sel_channels = utils.selectChannels()
        if len(sel_channels) == 0:
            utils.warningDialog(
                'No channels are avaliable in the Channel List')
            return False
        anim_dict = {}
        for p in sel_channels:
            anim_dict[str(p.name())] = self._jsonFromValue(
                0.0, p.eval())
        pose_name = re.sub(r'\W+', '_', self.le_cap_name.text())
        dir = os.path.join(hou.expandString(
            plglobals.lib_path), "pose", pose_name)
        object = sel_channels[0].node()
        while(type(object) is not hou.ObjNode):
            object = object.parent()
        if pose_name == 'gary':
            thumb.placeholder(os.path.join(dir, pose_name + '.jpg'))
            utils.warningDialog('Why would you name it that?...')
        else:
            ok = self._captureThumbnailStill(object, pose_name, dir)
            if not ok:
                return False
        self._writeToFile(anim_dict, pose_name, dir)
        self.capture.emit()

    def _jsonFromValue(self, time, value):
        return [{'time': time, 'value': value, 'slope': 0.0,
                 'inSlope': 0.0, 'accel': 0.0, 'accelRatio': 0,
                 'expression': 'bezier()', 'language': 'Hscript'}]

    def _writeToFile(self, data, name, dir):
        filename = os.path.join(dir, name)
        if not os.path.exists(dir):
            os.makedirs(dir)
        try:
            with gzip.open(filename, 'wt', encoding='UTF-8') as zipfile:
                json.dump(data, zipfile)
        except IOError as e:
            utils.warningDialog(f"Unable to write file.\nError: {e}")

    def _readFromFile(self, name, dir):
        filename = os.path.join(dir, name)
        try:
            with gzip.open(filename, 'rt', encoding='UTF-8') as zipfile:
                return json.load(zipfile)
        except IOError as e:
            utils.warningDialog(f"Unable to read file.\nError: {e}")
            return False

    def _captureThumbnailStill(self, object, pose_name, dir):
        if not os.path.isdir(dir):
            os.makedirs(dir)
        filename = os.path.join(dir, hou.expandString(f"{pose_name}.jpg"))
        self._captureThumbnail(hou.frame(), filename, object)

    def _captureThumbnailSequence(self, frames, object, clip_name, dir):
        cur_frame = hou.frame()
        img_filenames = []
        if not os.path.isdir(dir):
            os.makedirs(dir)
        self.cancel = False
        for i in range(int(frames[0]), int(frames[1])):
            hou.setFrame(i)
            filename = os.path.join(
                dir, hou.expandString(f"{clip_name}.$F4.jpg"))
            img_filenames.append(filename)
            ok = self._captureThumbnail(i, filename, object)
            assert ok
            if self.cancel:
                shutil.rmtree(dir)
                self.cancel = False
                return False
        hou.setFrame(cur_frame)
        self._convertImagesToGif(img_filenames)
        return True

    def _convertImagesToGif(self, filename_list):
        gif = []
        base_dir = os.path.dirname(filename_list[0])
        filename = os.path.basename(filename_list[0]).split(".")[0] + ".gif"
        filename = os.path.join(base_dir, filename)
        duration = (1.0/hou.fps())*1000
        for i in filename_list:
            image = Image.open(i)
            gif.append(image.convert("P", palette=Image.ADAPTIVE))
            os.remove(i)
        gif[0].save(filename, save_all=True,
                    optimize=False, append_images=gif[1:], loop=0, duration=duration)

    def _captureThumbnail(self, frame, filename, object):
        cur_desktop = hou.ui.curDesktop()
        desktop = cur_desktop.name()
        panetab = cur_desktop.paneTabOfType(hou.paneTabType.SceneViewer).name()
        refPlane = cur_desktop.paneTabOfType(
            hou.paneTabType.SceneViewer).referencePlane()
        grid = refPlane.isVisible()
        refPlane.setIsVisible(False)
        persp = cur_desktop.paneTabOfType(
            hou.paneTabType.SceneViewer).curViewport().name()
        camera_path = f"{desktop}.{panetab}.world.{persp}"
        temp = os.path.join(os.path.dirname(filename), "temp.jpg")
        if filename is not None:
            if object is False:
                hou.hscript(
                    f"viewwrite -R beauty -g 2.21 -f {frame} {frame} {camera_path} {temp}")
            else:
                hou.hscript(
                    f"viewwrite -v {object} -R beauty -g 2.21 -f {frame} {frame} {camera_path} {temp}")
        refPlane.setIsVisible(grid)
        if not os.path.isfile(temp):
            return False
        try:
            img = Image.open(temp)
            w, h = img.size
            crop = min(w, h)
            img2 = img.crop(((w - crop)//2,
                            (h - crop)//2,
                            (w + crop)//2,
                            (h + crop)//2)).resize((192, 192))
            img2.save(filename)
            os.remove(temp)
        except Exception as e:
            utils.warningDialog(f"Unable to save thumbnail\nError: {e}")
        return True

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.cancel = True
