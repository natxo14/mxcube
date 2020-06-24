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
Camera Beam Brick

[Description]

This brick displays and save for different zoom value a beam position.

[Properties]

zoom - string - MultiplePositions hardware object which reference the different
                zoom position and allows to save beam position for each of them

[Signals]

ChangeBeamPosition - (xpos,ypos) - emitted when beam position change for a
                                   given zoom value.
                                   The client must get the zoom hardware
                                   object to know the current zoom position.

[Slots]

getBeamPosition - position["ybeam"] - When a client want to know the current
                  position["zbeam"]   beam position, it can connect a signal
                                      to this slot. At return of its emit call
                                      the dictionnary passed as argument will
                                      be filled with the current beam position

beamPositionChanged - ybeam, zbeam - slot which should be connected to all
                                     client able to change beam position.
                                     Display numerically and save the new
                                     beam positions.

setBrickEnabled - isEnabled - slot to call to disable the brick (expert mode for example).

[Comments]

"""

import sys
import math
import logging

from gui.utils import Icons, Colors, QtImport
from gui.BaseComponents import BaseWidget


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "ESRF"

class ESRFCameraBeamBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # variables -----------------------------------------------------------

        self.first_time = True
        self.y_beam = None
        self.z_beam = None
        self.calibration = 0
        self.drawing = None
        self.drawing_mgr = None

        # Hardware objects ----------------------------------------------------
        self.zoom_motor_hwobj = None
        
        # Internal values -----------------------------------------------------
        self.step_editor = None
        self.move_step = 1
        self.demand_move = 0
        self.in_expert_mode = None
        self.position_history = []

        # Properties ----------------------------------------------------------
        self.add_property("zoom", "string", "")
        
        # Signals ------------------------------------------------------------
        self.define_signal("ChangeBeamPosition", ())
        
        # Slots ---------------------------------------------------------------
        self.define_slot("getBeamPosition", ())
        self.define_slot("beamPositionChanged", ())
        self.define_slot("setBrickEnabled", ())
        
        # Graphic elements ----------------------------------------------------
        self.main_groupbox = QtImport.QGroupBox("Beam Position", self)
        self.ui_widgets_manager = QtImport.load_ui_file("camera_beam_brick.ui")

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
       
        self.ui_widgets_manager.save_current_beam_pos_pushbutton.clicked.connect(
            self.save_beam_position
        )

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "zoom":
            if self.zoom_motor_hwobj is not None:
                self.disconnect(self.zoom_motor_hwobj, "positionReached",
                                self.zoom_changed)
                self.disconnect(self.zoom_motor_hwobj, "noPosition",
                                self.zoom_changed)

            self.zoom_motor_hwobj = self.get_hardware_object(new_value)

            if self.zoom_motor_hwobj is not None:
                self.connect(self.zoom_motor_hwobj, "positionReached",
                                self.zoom_changed)
                self.connect(self.zoom_motor_hwobj, "noPosition",
                                self.zoom_changed)

                self.init_interface()
                self.zoom_changed()
           
    def init_interface(self):
        if self.zoom_motor_hwobj is not None:
            positions = self.zoom_motor_hwobj.get_positions_names_list()
            self.ui_widgets_manager.beam_positions_table.setRowCount(len(positions))

            for i, position in enumerate(positions):
                aux = self.zoom_motor_hwobj.get_position_key_value(position, "beamx")
                if aux is None:
                    aux = "0"
                beamy = int(aux)
                aux = self.zoom_motor_hwobj.get_position_key_value(position, "beamy")
                if aux is None:
                    aux = "0"
                beamz = int(aux)

                if beamy is None:
                    beamy = "Not defined"
                if beamz is None:
                    beamz = "Not defined"

                zoom_column_item = QtImport.QTableWidgetItem(str(position))
                y_column_item = QtImport.QTableWidgetItem(str(beamy))
                z_column_item = QtImport.QTableWidgetItem(str(beamz))
                
                self.ui_widgets_manager.beam_positions_table.setItem(i, 0, zoom_column_item)
                self.ui_widgets_manager.beam_positions_table.setItem(i, 1, y_column_item)
                self.ui_widgets_manager.beam_positions_table.setItem(i, 2, z_column_item)
 
    def zoom_changed(self):
        pass
        
    def save_beam_position(self):
        """
        Doc
        """
        if self.zoom_motor_hwobj is not None:
            current_pos = self.zoom_motor_hwobj.getPosition()
            self.zoom_motor_hwobj.setPositionKeyValue(current_pos, "resox", str(self.YCalib))
            self.zoom_motor_hwobj.setPositionKeyValue(current_pos, "resoy", str(self.ZCalib))
        else:
            print(f"CameraCalibrationBrick--ARG--zoom_motor_hwobj is None")
               
    
    def clear_table(self):
        """
        Adapt
        """
        #table = self.ui_widgets_manager.findChild(QtI
        # mport.QTableWidget, "aligment_table")
        self.ui_widgets_manager.beam_positions_table.clearContents()
            