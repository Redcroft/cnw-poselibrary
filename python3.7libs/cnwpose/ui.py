import hou

from PySide2 import QtWidgets


class CaptureUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self._createMainLayout()

    def _createMainLayout(self):
        self.ui_label_a = QtWidgets.QLabel("Hello")
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.ui_label_a)
        self.setLayout(layout)
