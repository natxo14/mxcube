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
Camera Calibration Brick

[Description]

This brick allows to calibrate the display of a frame grabber.
The different features are:
    - 2 clicks calibration procedure using 2 motors displacement defined in
      the interface
    - Display of the calibration in both axis for different zoom values
    - Saving of the calibration of both axis for different zoom values

[Properties]

zoom - string - MultiplePositions hardware object which reference the different
                zoom position and allows to save calibration for both axis
                for each zoom positions

vertical motor - string - Motor used to calibrate vertical axis

horizontal motor - string - Motor used to calibrate horizontal axis

[Signals]

getView - {"drawing"} - emitted to get a reference on the image viewer object.
                        At returned of the emit function, the key "drawing"
                        exists and its value is the reference of the image
                        viewer or the key "drawing" does not exists which mean
                        that the image viewer object does not exists.

"ChangePixelCalibration" - (YCalib, ZCalib) - Emitted when pixel calibration
                                              change.

[Slots]

getCalibration - {"ycalib", "zcalib"} - Display the new pixel size calibration
                                        changed by another object

useExpertMode - get the expoert mode signal:
                  - Disables the brick in non-expert mode.

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

class ESRFCameraCalibrationBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # variables -----------------------------------------------------------

        self.first_time = True
        self.y_calib = None
        self.z_calib = None
        self.calibration = 0
        self.drawing = None
        self.y1 = 0
        self.z1 = 0
        self.y2 = 0
        self.z2 = 0
        self.drawing_mgr = None

        # Hardware objects ----------------------------------------------------
        self.zoom_motor_hwobj = None
        self.h_motor_hwobj = None
        self.v_motor_hwobj = None

        # Internal values -----------------------------------------------------
        self.step_editor = None
        self.move_step = 1
        self.demand_move = 0
        self.in_expert_mode = None
        self.position_history = []

        # Properties ----------------------------------------------------------
        self.add_property("zoom", "string", "")
        self.add_property("vertical motor", "string", "")
        self.add_property("horizontal motor", "string", "")
        
        # Signals ------------------------------------------------------------
        self.define_signal("getView", ())
        self.define_signal("getBeamPosition", ())

        # Slots ---------------------------------------------------------------
        self.define_slot("changePixelScale", ())
        
        # Graphic elements ----------------------------------------------------
        self.main_groupbox = QtImport.QGroupBox("Pixel Size Calibration", self)
        self.manager_widget = QtImport.load_ui_file("camera_calibration.ui")

        #validator for input values for delta phi: min/max/decimals
        # self.manager_widget.delta_phi_textbox.setValidator(
        #     QtImport.QDoubleValidator(0, 180, 2)
        # )

        # Layout --------------------------------------------------------------
        _groupbox_vlayout = QtImport.QVBoxLayout(self)
        _groupbox_vlayout.addWidget(self.manager_widget)
        _groupbox_vlayout.setSpacing(0)
        _groupbox_vlayout.setContentsMargins(0, 0, 0, 0)
        self.main_groupbox.setLayout(_groupbox_vlayout)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.main_groupbox)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(_main_vlayout)

        # Qt signal/slot connections ------------------------------------------
       
        self.manager_widget.save_calibration_pushbutton.clicked.connect(
            self.save_calibration
        )

        self.manager_widget.start_new_calibration_pushbutton.clicked.connect(
            self.start_new_calibration
        )

        self.manager_widget.number_points_spinbox.valueChanged.connect(
            self.change_point_number
        )

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "zoom":
            
            if self.zoom_motor_hwobj is not None:
            self.disconnect(self.zoom_motor_hwobj, "positionReached", self.zoom_changed)
            self.disconnect(self.zoom_motor_hwobj, "noPosition", self.zoom_changed)
            self.disconnect(self.zoom_motor_hwobj, "stateChanged", self.zoom_state_changed)

                if new_value is not None:
                    self.zoom_motor_hwobj = self.get_hardware_object(new_value)
                    
                if self.zoom_motor_hwobj is None:
                    # first time motor is set
                    try:
                        step = float(self.default_step)
                    except BaseException:
                        try:
                            step = self.zoom_motor_hwobj.GUIstep
                        except BaseException:
                            step = 1.0
                    self.set_line_step(step)

                if self.zoom_motor_hwobj is not None:
                    self.connect(self.zoom_motor_hwobj, "positionReached", self.zoom_changed)
                    self.connect(self.zoom_motor_hwobj, "noPosition", self.zoom_changed)
                    self.connect(self.zoom_motor_hwobj, "stateChanged", self.state_changed)

        if property_name == "vertical motor":
            self.v_motor_hwobj = self.get_hardware_object(new_value)
            name = self.h_motor_hwobj.name()
            #TODO : set label on GUI with motor name
            # self.relZLabel.setText("Delta on \"%s\" "%mne)
            # self.vmotUnit = self.vmot.getProperty("unit")
            # if self.vmotUnit is None:
            #     self.vmotUnit = 1e-3
        if property_name == "horizontal motor":
            self.h_motor_hwobj = self.get_hardware_object(new_value)
            #TODO : set label on GUI

    def save_calibration(self):
        """
        Doc
        """
        if self.zoom_motor_hwobj is not None:
            currentPos = self.zoom_motor_hwobj.getPosition()
            self.zoom_motor_hwobj.setPositionKeyValue(currentPos, "resox", str(self.YCalib))
            self.zoom_motor_hwobj.setPositionKeyValue(currentPos, "resoy", str(self.ZCalib))
        else:
            print(f"CameraCalibrationBrick--ARG--zoom_motor_hwobj is None")
                
    def start_new_calibration(self):
        """
        Doc
        """
        if self.calibration == 0:

            if self.drawingMgr is not None:
                self.calibration = 1
                self.calibButton.setText("Cancel Calibration")

                self.drawingMgr.startDrawing()

        elif self.calibration == 1:
            self.calibration = 0
            self.calibButton.setText("Start New Calibration")
            self.drawingMgr.stopDrawing()
            self.drawingMgr.hide()

        elif self.calibration == 2:
            self.disconnect(self.vmot, qt.PYSIGNAL("moveDone"),
                            self.moveFinished)
            self.disconnect(self.hmot, qt.PYSIGNAL("moveDone"),
                            self.moveFinished)
            self.hmot.stop()
            self.vmot.stop()
            self.calibration = 0
            self.calibButton.setText("Start New Calibration")
            self.drawingMgr.stopDrawing()
            self.drawingMgr.hide()
    
    def change_point_number(self, new_point_number):
        """
        Adapt
        """
        self.points_for_aligment = self.manager_widget.number_points_spinbox.value()
        self.manager_widget.aligment_table.setRowCount(self.points_for_aligment)

    def clear_table(self):
        """
        Adapt
        """
        #table = self.manager_widget.findChild(QtI
        # mport.QTableWidget, "aligment_table")
        table = self.manager_widget.aligment_table
        self.points_for_aligment = self.manager_widget.number_points_spinbox.value()
        table.setRowCount(self.points_for_aligment)
        table.clearContents()
            