import hou
import sys
from PySide2 import QtWidgets
from PySide2 import QtCore
from . import utils


class _NodeTextField(QtWidgets.QLineEdit):
    """Text field for storing the node path."""

    def dropEvent(self, event):
        """Handle data dropped on the field."""
        self.setText("")
        QtWidgets.QLineEdit.dropEvent(self, event)

class NodeChooserWidget(QtWidgets.QWidget):
    """Widget for choosing a node."""

    # custom signal
    nodeChanged = QtCore.Signal(str, str)

    # Static constants
    MAX_RECENTS = 5

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)

        # create main layout
        self._createLayout()

        self._eventTypes = (
            hou.nodeEventType.NameChanged,
            hou.nodeEventType.BeingDeleted)

        # Initialize defaults
        self.reset()

    def cleanup(self):
        self.setParent(None)
        self._nodeMenu.removeEventFilter(self)
        self.disconnect(None, None, None)
        self._removeCallbacks()

    def reset(self):
        self._node = None
        self._nodeHistory = {}
        self._nodeField.setText("")
        self._clearHistory()

    def _createLayout(self):
        self._nodeField = _NodeTextField()
        self._nodeField.textChanged.connect(
            self._handleNodeFieldChanged)
        self._nodeField.editingFinished.connect(
            self._handleNodeFieldEdited)

        self._noHistoryAction = QtWidgets.QAction("<No History>", self)
        self._noHistoryAction.setEnabled(False)
        self.clearHistoryAction = QtWidgets.QAction("<Clear History>", self)
        self.clearHistoryAction.triggered.connect(self._clearHistory)
        self._nodeMenu = QtWidgets.QMenu()
        self._nodeMenu.setStyleSheet(hou.qt.styleSheet())
        self._nodeMenu.addAction(self._noHistoryAction)
        self._nodeMenu.installEventFilter(self)

        self._nodeHistoryButton = \
            hou.qt.createMenuButton(self._nodeMenu)

        chooser_button = hou.qt.NodeChooserButton()
        chooser_button.setNodeChooserFilter(hou.nodeTypeFilter.Sop)
        chooser_button.nodeSelected.connect(self._handleNodeSelected)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._nodeField, stretch=1)
        layout.addWidget(self._nodeHistoryButton)
        layout.addSpacing(5)
        layout.addWidget(chooser_button)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def ensureNodeSelected(self):
        """Checks if a valid node is present and promts the user to
        select one if needed.

        Return selected node if any, and None otherwise.
        """
        if self._node is not None:
            return self._node

        ok = utils.warningDialog(
            "No node selected. Please choose a node...")
        if not ok:
            return None

        # Prompt the user to select a node node.
        path = hou.ui.selectNOde(relative_to_node=None,
                                 initial_node=None,
                                 node_type_filter=hou.nodeTypeFilter.Obj)
        if path is None:
            return None

        success = self.setNode(path)
        if not success:
            return None

        return self._node

    def selectedNode(self):
        return self._node

    def setNode(self, path):
        """Sets the current node to that at the given path.
    
        Return the True if node was successfully selected and Falte otherwise.
        """
        if self._node and self._node.path() == path:
            return True

        node = hou.node(path)
        if node is None:
            return False

        self._addHistory(path)
        self._nodeField.setText(path)

        old_node_path = None
        if self._node is not None:
            old_node_path = self._node.path()
        self.nodeChanged.emit(path, old_node_path)

        self._removeCallbacks()

        self._node = node
        self._node.addEventCallback(self._eventTypes, self._nodeEvent)

        return True

    def eventFilter(self, widget, event):
        if sys.platform != "macosc":
            return False

        if event.type() == QtCore.QEvent.Show\
           and widget is self._nodeMenu:

            button_geom = self._nodeHistoryButton.geometry()
            frame_geom = self.geometry()
            menu_geom = self._nodeMenu.sizeHint()

            menu_x = button_geom.x()
            menu_y = button_geom.y() + button_geom.height()

            menu_extent = menu_x + menu_geom.width()
            if menu_extent >= frame_geom.width() - 5:
                menu_x -= menu_extent - frame_geom.width() - 5

            pos = QtCore.QPoint(menu_x, menu_y)
            self._nodeHistoryButton.menu().move(pos)
            return True

        return False

    def _nodeEvent(self, **kwargs):
        if kwargs["event_type"] is hou.nodeEventType.BeingDeleted:
            self.nodeChanged.emit('',self._node.path())
            self._nodeField.setText("")
            self._node = None
        elif kwargs["event_type"] is hou.nodeEventType.NameChanged:
            self._nodeField.setText(kwargs["node"].path())

    def _removeCallbacks(self):
        if self._node:
            self._node.removeEventCallback(self._eventTypes, self._nodeEvent)

    def _addHistory(self, path):
        path_action = QtWidgets.QAction("1. %s" % path, self)
        path_action.triggered.connect(self._handleNodeHistorySelection)
        self._nodeHistory[path_action] = path

        # Avoid duplicates
        for action in self._nodeMenu.actions():
            if action in self._nodeHistory\
               and self._nodeHistory[action] == path:
                self._nodeMenu.removeAction(action)
                del self._nodeHistory[action]

        menu_actions = self._nodeMenu.actions()
        if len(menu_actions) == 1:
            self._nodeMenu.clear()
            self._nodeMenu.addSeparator()
            self._nodeMenu.addAction(self.clearHistoryAction)

        elif len(menu_actions) > NodeChooserWidget.MAX_RECENTS:
            self._nodeMenu.removeAction(menu_actions[-1])

        # Insert node at the top of the menu
        self._nodeMenu.insertAction(self._nodeMenu.actions()[0], path_action)

        # Update history action labels to include numbering
        for idx, action in enumerate(self._nodeMenu.actions()):
            if action in self._nodeHistory:
                path = self._nodeHistory[action]
                action.setText("%i. %s" % (idx + 1, path))

    def _clearHistory(self):
        self._nodeHistory.clear()
        self._nodeMenu.clear()
        self._nodeMenu.addAction(self._noHistoryAction)

    def _handleNodeHistorySelection(self):
        clicked_action = self.sender()
        path = self._nodeHistory[clicked_action]
        self.setNode(path)

    def _handleNodeFieldChanged(self):
        # We only handle node path changes if the field is *not* in focus
        # (i.e. drag-and-drop onto the field)
        if self._nodeField.hasFocus():
            return

        node_path = self._nodeField.text()
        self.setNode(node_path)

    def _handleNodeFieldEdited(self):
        node_path = self._nodeField.text()
        if len(node_path.strip()) == 0 and self._node:
            # Reset the node field to path of current node
            self._nodeField.setText(self._node.path())
            return

        self.setNode(node_path)

    def _handleNodeSelected(self, node):
        """Handle a selected node change."""
        if node is None:
            utils.warningDialog("The selected node is invalid",
                                show_cancel=False)
            return

        self._nodeField.setText(node.path())
        self.setNode(node.path())
