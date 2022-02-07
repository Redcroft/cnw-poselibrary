import hou

# Global Variables
global lib_path
lib_path = hou.expandString('$HIP/Poses/')
global debug
debug = 1
global clip
clip = {"name": '', "dir": '', "type": ''}

# User Variables
CAP_HELP_TEXT = '''Select the channels in the Animation Editor Channel List.Select the Time Range in the timeline.'''
