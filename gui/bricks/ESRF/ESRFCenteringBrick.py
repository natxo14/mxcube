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
[Name] Centering Brick

[Description]


[Properties]
-----------------------------------------------------------------------
| name         | type   | description
-----------------------------------------------------------------------
| blah      | string | 
| blah | string | 
-----------------------------------------------------------------------

[Signals] -

[Slots] -

[Comments] -

[Hardware Objects]
-----------------------------------------------------------------------
| name         | signals             | functions
-----------------------------------------------------------------------
|          | signal0     | function0()
|  	       
-----------------------------------------------------------------------
"""

import sys
import math
import logging

from gui.utils import Icons, Colors, QtImport
from gui.BaseComponents import BaseWidget


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "ESRF"

class ESRFCenteringBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.diffractometer_hwobj = None

        # Internal values -----------------------------------------------------
        self.step_editor = None
        self.move_step = 1
        self.demand_move = 0
        self.in_expert_mode = None
        self.position_history = []
        self.points_for_aligment = 0

        # Properties ----------------------------------------------------------
        self.add_property("mnemonic", "string", "")
        self.add_property("clockwise", "boolean", False)
        self.add_property("table_y_inverted", "boolean", False)
        self.add_property("table_z_inverted", "boolean", False)

        # Signals ------------------------------------------------------------
        self.define_signal("getView", ())
        self.define_signal("getBeamPosition", ())

        # Slots ---------------------------------------------------------------
        self.define_slot("changePixelScale", ())
        
        # Graphic elements ----------------------------------------------------
        self.main_groupbox = QtImport.QGroupBox("Graphics items", self)
        self.ui_widgets_manager = QtImport.load_ui_file("centering.ui")

        
        #validator for input values for delta phi: min/max/decimals
        # self.ui_widgets_manager.delta_phi_textbox.setValidator(
        #     QtImport.QDoubleValidator(0, 180, 2)
        # )

        # Layout --------------------------------------------------------------
        _groupbox_vlayout = QtImport.QVBoxLayout(self)
        _groupbox_vlayout.addWidget(self.ui_widgets_manager)
        _groupbox_vlayout.setSpacing(0)
        _groupbox_vlayout.setContentsMargins(0, 0, 0, 0)
        self.main_groupbox.setLayout(_groupbox_vlayout)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.main_groupbox)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(_main_vlayout)

        # Qt signal/slot connections ------------------------------------------
       
        self.ui_widgets_manager.show_center_checkbox.stateChanged.connect(
            self.show_center
        )

        self.ui_widgets_manager.show_help_line_checkbox.stateChanged.connect(
            self.show_help_lines
        )

        self.ui_widgets_manager.number_points_spinbox.valueChanged.connect(
            self.change_point_number
        )

        self.ui_widgets_manager.start_alignment_button.clicked.connect(
            self.start_aligment
        )

        self.ui_widgets_manager.cancel_alignment_button.clicked.connect(
            self.cancel_aligment
        )

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "mnemonic":
            self.diffractometer_hwobj = self.get_hardware_object(new_value)
            
            equipment = self.get_hardware_object(new_value)
            if equipment is not None :
                    xoryMotor = equipment.getDeviceByRole('horizontal')
                    if xoryMotor is not None:
                        self.__verticalPhi = True
                    else:
                        xoryMotor = equipment.getDeviceByRole('vertical')
                        if xoryMotor is None:
                            logging.getLogger().error('%s: could not find motors horizontal nor vertical motor in Hardware Objects %s',
                                                      str(self.name()),equipment.name())
                            return
                        self.__verticalPhi = False

                    zMotor = equipment.getDeviceByRole('inBeam')
                    rMotor = equipment.getDeviceByRole('rotation')
                    if zMotor is None or rMotor is None :
                        logging.getLogger().error('%s: could not find motors inBeam or rotation motor in Hardware Objects %s',
                                                  str(self.name()),equipment.name())
                        return          

    def show_center(self, checkbox_state):
        """
        Doc
        """
        pass
    def show_help_lines(self, checkbox_state):
        """
        Doc
        """
        pass
    def start_aligment(self):
        """
        Launch aligment process
        """
        pass
    def cancel_aligment(self):
        """
        Cancel aligment process
        """
        pass

    def change_point_number(self, new_point_number):
        """
        Adapt
        """
        self.points_for_aligment = self.ui_widgets_manager.number_points_spinbox.value()
        self.ui_widgets_manager.aligment_table.setRowCount(self.points_for_aligment)

    def clear_table(self):
        """
        Adapt
        """
        #table = self.ui_widgets_manager.findChild(QtI
        # mport.QTableWidget, "aligment_table")
        table = self.ui_widgets_manager.aligment_table
        self.points_for_aligment = self.ui_widgets_manager.number_points_spinbox.value()
        table.setRowCount(self.points_for_aligment)
        table.clearContents()
            