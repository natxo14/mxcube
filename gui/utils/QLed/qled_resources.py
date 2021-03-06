#pylint: skip-file

import sys
from gui.utils import QtImport

if QtImport.qt_variant == "PyQt4":
    if sys.version_info[0] == 3:
        from gui.utils.QLed.qled_resources_qt4_py3 import *
    else:
        from gui.utils.QLed.qled_resources_qt4 import *
elif QtImport.qt_variant == "PyQt5":
    if sys.version_info[0] == 3:
        from gui.utils.QLed.qled_resources_qt5_py3 import *
    else:
        from gui.utils.QLed.qled_resources_qt5 import *
elif QtImport.qt_variant == "PySide":
    if sys.version_info[0] == 3:
        from gui.utils.QLed.qled_resources_pyside_py3 import *
    else:
        from gui.utils.QLed.qled_resources_pyside import *
