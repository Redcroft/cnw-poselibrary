import hou


def warningDialog(message, true_button='OK', false_button='Cancel',
                  show_cancel=True):
    """Create a warning dialog with the given properties
    and return if true_button or Ok was pressed.
    """
    if show_cancel:
        btns = (true_button, false_button)
        def_choice = 1
    else:
        btns = (true_button,)
        def_choice = 0
    warning = hou.ui.displayMessage(
        message,
        buttons=btns,
        severity=hou.severityType.ImportantMessage,
        default_choice=def_choice,
        close_choice=1)
    return True if warning == 0 else False
