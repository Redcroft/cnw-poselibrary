import hou
import os
import sys
from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
from . import utils
from . import plglobals

# rgb(185, 134, 32) - solid boder
# rgba(185, 134, 32, 77) - fill

if plglobals.debug == 1:
    from importlib import reload
    reload(plglobals)


StyleSheet = '''
QLabel {
    margin: 0px;
}

QImageThumbnail {
    background: rgba(0, 0, 0, 10%);
    border: 1px solid rgb(0, 0, 0);
    margin: 2px;
}

QImageThumbnail:hover {
    background: rgba(255, 255, 255, 45%);
}

QImageThumbnail:selected {
    background: rgba(255, 192, 23, 45%);
}
'''


class FlowLayout(QtWidgets.QLayout):
    def __init__(self, parent=None, margin=-1, hspacing=-1, vspacing=-1):
        super(FlowLayout, self).__init__()
        self._hspacing = hspacing
        self._vspacing = vspacing
        self._items = []
        self.setContentsMargins(margin, margin, margin, margin)

    def __del__(self):
        del self._items[:]

    def addItem(self, item):
        self._items.append(item)

    def horizontalSpacing(self):
        if self._hspacing >= 0:
            return self._hspacing
        else:
            return self.smartSpacing(
                QtWidgets.QStyle.PM_LayoutHorizontalSpacing)

    def verticalSpacing(self):
        if self._vspacing >= 0:
            return self._vspacing
        else:
            return self.smartSpacing(
                QtWidgets.QStyle.PM_LayoutVerticalSpacing)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)

    def expandingDirections(self):
        return QtCore.Qt.Orientations(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QtCore.QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        left, top, right, bottom = self.getContentsMargins()
        size += QtCore.QSize(left + right, top + bottom)
        return size

    def doLayout(self, rect, testonly):
        left, top, right, bottom = self.getContentsMargins()
        width = right - left
        effective = rect.adjusted(+left, +top, -right, -bottom)
        x = effective.x()
        y = effective.y()
        lineheight = 0
        for item in self._items:
            widget = item.widget()
            hspace = self.horizontalSpacing()
            if hspace == -1:
                hspace = widget.style().layoutSpacing(
                    QtWidgets.QSizePolicy.PushButton,
                    QtWidgets.QSizePolicy.PushButton, QtCore.Qt.Horizontal)
            vspace = self.verticalSpacing()
            if vspace == -1:
                vspace = widget.style().layoutSpacing(
                    QtWidgets.QSizePolicy.PushButton,
                    QtWidgets.QSizePolicy.PushButton, QtCore.Qt.Vertical)
            nextX = x + item.sizeHint().width() + hspace
            if nextX - hspace > effective.right() and lineheight > 0:
                x = effective.x()
                y = y + lineheight + vspace
                nextX = x + item.sizeHint().width() + hspace
                lineheight = 0
            if not testonly:
                item.setGeometry(
                    QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))
            x = nextX
            lineheight = max(lineheight, item.sizeHint().height())
        return y + lineheight - rect.y() + bottom

    def smartSpacing(self, pm):
        parent = self.parent()
        if parent is None:
            return -1
        elif parent.isWidgetType():
            return parent.style().pixelMetric(pm, None, parent)
        else:
            return parent.spacing()


class ResizableScrollArea(QtWidgets.QScrollArea):
    def _init__(self, parent=None):
        supe(ResizableScrollArea, self).__init__(parent)

    def resizeEvent(self, event):
        wrapper = self.findChild(QtWidgets.QWidget)
        flow = wrapper.findChild(FlowLayout)

        if wrapper and flow:
            width = self.viewport().width()
            height = flow.heightForWidth(width)
            size = QtCore.QSize(width, height)
            point = self.viewport().rect().topLeft()
            flow.setGeometry(QtCore.QRect(point, size))
            self.viewport().update()

        super(ResizableScrollArea, self).resizeEvent(event)


class ScrollingFlowWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ScrollingFlowWidget, self).__init__(parent)
        grid = QtWidgets.QGridLayout(self)
        scroll = ResizableScrollArea()
        self._wrapper = QtWidgets.QWidget(scroll)
        self.flow_layout = FlowLayout(self._wrapper)
        self._wrapper.setLayout(self.flow_layout)
        scroll.setWidget(self._wrapper)
        scroll.setWidgetResizable(True)
        grid.addWidget(scroll)

    def addWidget(self, widget):
        self.flow_layout.addWidget(widget)
        widget.setParent(self._wrapper)

    def count(self):
        return self.flow_layout.count()

    def itemAt(self, index):
        return self.flow_layout.itemAt(index)


class QImageThumbnail(QtWidgets.QWidget):
    clicked = QtCore.Signal(QtCore.Qt.MouseButton)
    label_text = ''
    name = ''
    path = ''
    clip_type = ''
    thumb_type = ''

    def __init__(self):
        super(QImageThumbnail, self).__init__()
        self.setStyleSheet(hou.qt.styleSheet())
        self.setStyleSheet(StyleSheet)

        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)
        self.thumbnail = QtWidgets.QLabel()
        self.thumbnail.setScaledContents(True)
        self.label = QtWidgets.QLabel()
        self.label.setFixedHeight(22)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.thumbnail, 0, 0)
        layout.addWidget(self.label, 1, 0)
        self.thumbnail.adjustSize()
        self.setStyleSheet(StyleSheet)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_click)
        self.installEventFilter(self)

    def __del__(self):
        self.thumbnail.clear()
        self.thumbnail.setParent(None)
        self.label.setParent(None)
        self.setParent(None)

    def name(self):
        return self.name

    def setPath(self, path):
        self.path = path
        self.name = os.path.basename(path)

    def setType(self, clip_type):
        self.clip_type = clip_type

    def setText(self, text):
        self.label_text = text.replace("_", " ")
        self.label.setText(text)

    def setMovie(self, gif):
        self.thumb_type = 'movie'
        self.movie = QtGui.QMovie(gif)
        self.movie.setParent(self.thumbnail)
        self.thumbnail.setMovie(self.movie)
        self.movie.jumpToFrame(0)

    def setImage(self, jpg):
        self.thumb_type = 'pixmap'
        self.thumbnail.setPixmap(jpg)

    def resizeEvent(self, event):
        self.formatText()
        super(QImageThumbnail, self).resizeEvent(event)

    def formatText(self):
        width = self.label.width()
        text = self.label_text
        fw = QtGui.QFontMetrics(self.font()).averageCharWidth()
        # fw = fm.averageCharWidth()
        num = int(width / fw)
        if len(text) > num:
            self.label.setText(self.label_text[:num] + '...')
        else:
            self.label.setText(self.label_text)

    def paintEvent(self, event):
        option = QtWidgets.QStyleOption()
        option.initFrom(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtWidgets.QStyle.PE_Widget, option, painter, self)

    def mousePressEvent(self, event):
        plglobals.clip['name'] = self.name
        plglobals.clip['dir'] = self.path
        plglobals.clip['type'] = self.clip_type
        self.clicked.emit(event.button())

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.HoverEnter:
            if self.thumb_type == 'movie':
                self.movie.start()
            self.label.setStyleSheet('color: black')
        if event.type() == QtCore.QEvent.HoverLeave:
            if self.thumb_type == 'movie':
                self.movie.jumpToFrame(0)
                self.movie.stop()
            self.label.setStyleSheet('color: rgb(204, 204, 204)')
        return QtWidgets.QWidget.eventFilter(self, obj, event)

    def right_click(self, pos):
        menu = QtWidgets.QMenu()
        menu.setStyleSheet(hou.qt.styleSheet())

        delete_option = menu.addAction('Delete')
        rename_option = menu.addAction('Rename')

        delete_option.triggered.connect(self._del_clip)

        hello_option.triggered.connect(
            lambda: self.label.setText('Hello World'))
        test_option.triggered.connect(
            lambda: self.label.setText('Testing my custom widget'))

        menu.exec_(self.mapToGlobal(pos))
