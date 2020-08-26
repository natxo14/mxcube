#
#  Project: MXCuBE
#  https://github.com/mxcube
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.
"""
ESRF ID13 Export Data Brick

[Description]

This brick exports data to different files:

Exported data:
    * Information related to microscope status:
        * motor positions
        * camera calibration
    * Information on graphical items:
        * beam position
        * created points/lines/ROI's positions
    * Microscope snapshots

Created files:
    * JSON file with 
    * Image file with raw microscope image
    * Image file with microscope image plus graphics items (if any)

[Properties]

xml file

[Signals]



[Slots]

sample_changed - sample changed from outside GUI


[Comments]

"""

import sys
import math
import logging
import os

import copy
from gui.utils import Icons, Colors, QtImport
from gui.BaseComponents import BaseWidget
from HardwareRepository import HardwareRepository as HWR

from bliss.config import static
from bliss.config import get_sessions_list

try:
    from xml.etree import cElementTree  # python2.5
except ImportError:
    import cElementTree

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "ESRF"

class ESRFID13ExportDataBrick(BaseWidget):

    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Slots ---------------------------------------------------------------
        self.define_slot("sample_changed", ())

        
        # Graphic elements ----------------------------------------------------
        self.main_groupbox = QtImport.QGroupBox("Beam Configuration", self)
        self.ui_widgets_manager = QtImport.load_ui_file("esrf_id13_configuration_widget.ui")
