import hou
from PySide2 import QtWidgets

from . import plglobals

if plglobals.debug == 1:
    from importlib import reload
    reload(plglobals)


class UI(QtWidgets.QWidget):
    """ Contains all the widgets to create a capture interface."""

    def __init__(self, parent=None):
        super(UI, self).__init__()
        self.setFixedHeight(hou.ui.scaledSize(80))

        self._createUI()

    def _createUI(self):
        # Library Directory selector widgets
        self.le_lib_dir = QtWidgets.QLineEdit()
        self.le_lib_dir.setText('$HIP/')
        btn_lib_dir = hou.qt.FileChooserButton()
        btn_lib_dir.setFileChooserTitle(
            'Choose Animation Library Directory...')
        btn_lib_dir.setFileChooserFilter(hou.fileType.Directory)
        btn_lib_dir.setFileChooserMode(hou.fileChooserMode.Read)
        btn_lib_dir.fileSelected.connect(self._onLibDirSelected)

        lib_dir_sub_layout = QtWidgets.QHBoxLayout()
        lib_dir_sub_layout.addWidget(self.le_lib_dir)
        lib_dir_sub_layout.addWidget(btn_lib_dir)

        lib_dir_layout = QtWidgets.QFormLayout()
        lib_dir_layout = QtWidgets.QFormLayout()
        lib_dir_layout.addRow(QtWidgets.QLabel(
            'Library Directory '), lib_dir_sub_layout)

        group_box = QtWidgets.QGroupBox()
        group_box.setLayout(lib_dir_layout)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(group_box)
        self.setLayout(layout)

    def _onLibDirSelected(self, file_path):
        if file_path:
            self.le_lib_dir.setText(str(file_path))
            plglobals.lib_path = str(hou.expandString(file_path))
