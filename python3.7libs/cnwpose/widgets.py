import hou
import sys
from PySide2 import QtWidgets
from PySide2 import QtCore
from . import utils


StyleSheet = '''
QWidget {
    margin: 5px;
}

QWidget:hover {
    background: rgba(255, 255, 255, 45%);
}

QWidget:selected {
    border: 1px solid rgb(185, 134, 32);
    border-radius: 1px;
    colorY rgb(204, 204, 204);
    background: rgba(185, 134, 32, 77);
}
'''


class QImageThumbnail(QtWidgets.QWidget):
    def __init__(self):
        super(QImageThumbnail, self).__init__()
        self.setStyleSheet(hou.qt.styleSheet())
        self.setStyleSheet(StyleSheet)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.label = QtWidgets.QLabel('Testing my custom widget')
        layout.addWidget(self.label)
        self.setStyleSheet(StyleSheet)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_click)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            obj.setAttribute(QtCore.Qt.WA_Hover, True)
            print(obj.getAttribute(QtCore.Qt.WA_Hover))
        return QtWidgets.QWidget.eventFilter(self, obj, event)

    def right_click(self, pos):
        menu = QtWidgets.QMenu()
        menu.setStyleSheet(hou.qt.styleSheet())

        hello_option = menu.addAction('Hello World')
        test_option = menu.addAction('Testing my custom widget')
        new_option = menu.addAction('Yes')

        hello_option.triggered.connect(
            lambda: self.label.setText('Hello World'))
        test_option.triggered.connect(
            lambda: self.label.setText('Testing my custom widget'))

        menu.exec_(self.mapToGlobal(pos))
