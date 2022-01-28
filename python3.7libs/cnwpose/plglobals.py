import hou

# Global Variables
global lib_path
lib_path = hou.expandString('$HIP')
global debug
debug = 1

# User Variables
CAP_HELP_TEXT = '''Select the channels in the Animation Editor you wish to capture along with the selected time range in the timeline. If no range is selected it will capture the current frame as a pose.'''
