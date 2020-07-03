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

from HardwareRepository import HardwareRepository as HWR
from HardwareRepository.HardwareObjects import sample_centring


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
        self.current_calibration_procedure = None

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
        self.ui_widgets_manager = QtImport.load_ui_file("camera_calibration.ui")

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
       
        self.ui_widgets_manager.save_calibration_pushbutton.clicked.connect(
            self.save_calibration
        )

        self.ui_widgets_manager.start_new_calibration_pushbutton.clicked.connect(
            self.start_new_calibration
        )

        # Other hardware object connections --------------------------
        self.connect(
            HWR.beamline.diffractometer,
            "new_calibration_done",
            self.diffractometer_manual_calibration_done,
        )

    def property_changed(self, property_name, old_value, new_value):
        print(f"cameraCalibBrick property_changed {new_value}")
        if property_name == "zoom":
            
            if self.zoom_motor_hwobj is not None:
                self.disconnect(self.zoom_motor_hwobj, "positionReached", self.zoom_changed)
                self.disconnect(self.zoom_motor_hwobj, "noPosition", self.zoom_changed)
                self.disconnect(self.zoom_motor_hwobj, "stateChanged", self.zoom_state_changed)

            if new_value is not None:
                self.zoom_motor_hwobj = self.get_hardware_object(new_value)
                
            # if self.zoom_motor_hwobj is None:
            #     # first time motor is set
            #     try:
            #         step = float(self.default_step)
            #     except BaseException:
            #         try:
            #             step = self.zoom_motor_hwobj.GUIstep
            #         except BaseException:
            #             step = 1.0
            #     self.set_line_step(step)

            if self.zoom_motor_hwobj is not None:
                self.connect(self.zoom_motor_hwobj, "positionReached", self.zoom_changed)
                self.connect(self.zoom_motor_hwobj, "noPosition", self.zoom_changed)
                            
            self.update_gui()

        if property_name == "vertical motor":
            self.v_motor_hwobj = self.get_hardware_object(new_value)
            name = self.v_motor_hwobj.name()
            self.ui_widgets_manager.delta_z_label.setText(f"Delta on {name}:")
            #TODO : set label on GUI with motor name
            # self.relZLabel.setText("Delta on \"%s\" "%mne)
            # self.vmotUnit = self.vmot.getProperty("unit")
            # if self.vmotUnit is None:
            #     self.vmotUnit = 1e-3
        if property_name == "horizontal motor":
            self.h_motor_hwobj = self.get_hardware_object(new_value)
            name = self.h_motor_hwobj.name()
            self.ui_widgets_manager.delta_y_label.setText(f"Delta on {name}:")
            #TODO : set label on GUI
    
    def update_gui(self):
        if self.zoom_motor_hwobj is not None:
            positions = self.zoom_motor_hwobj.get_positions_names_list()
            self.ui_widgets_manager.calibration_table.setRowCount(len(positions))
            for i, position in enumerate(positions):
            # for i,  in range(pos):
                aux = self.zoom_motor_hwobj.get_position_key_value(position, "resox")
                if aux is None:
                    aux = "1"
                resoy = abs(int(aux * 1e9))
                aux = self.zoom_motor_hwobj.get_position_key_value(position, "resoy")
                if aux is None:
                    aux = "1"
                resoz = abs(int(aux * 1e9))
                

                if resoy is None:
                    resoy = "Not defined"
                if resoz is None:
                    resoz = "Not defined"

                """
                resolution are displayed in nanometer and saved in merter
                """

                zoom_column_item = QtImport.QTableWidgetItem(str(position))
                y_column_item = QtImport.QTableWidgetItem(str(resoy))
                z_column_item = QtImport.QTableWidgetItem(str(resoz))

                self.ui_widgets_manager.calibration_table.setItem(i, 0, zoom_column_item)
                self.ui_widgets_manager.calibration_table.setItem(i, 1, y_column_item)
                self.ui_widgets_manager.calibration_table.setItem(i, 2, z_column_item)

    def get_zoom_index(self, position_to_find):
        if self.zoom_motor_hwobj is not None:
            positions = self.zoom_motor_hwobj.get_positions_names_list()
            for i, position in enumerate(positions):
                if position_to_find == position:
                    return(i)
            return(-1)

    def zoom_changed(self):
        if self.zoom_motor_hwobj is not None:
            current_pos = self.zoom_motor_hwobj.get_value()
            self.curr_idx = self.get_zoom_index(current_pos)
            
            if len(self.ui_widgets_manager.calibration_table.selectedItems()) != 0:
                self.ui_widgets_manager.calibration_table.selectionMode().clearSelection()
                
            if self.curr_idx != -1:
                aux = self.zoom_motor_hwobj.get_position_key_value(current_pos, "resox")
                if aux is None:
                    aux = "1"
                resoy = float(aux)
                aux = self.zoom_motor_hwobj.get_position_key_value(current_pos, "resoy")
                if aux is None:
                    aux = "1"
                resoz = float(aux)

                if resoy is None:
                    self.y_calib = None
                    resoy = "Not defined"
                else:
                    self.y_calib = resoy
                    resoy = str(int(resoy * 1e9))
                
                if resoz is None:
                    self.z_calib = None
                    resoz = "Not defined"
                else:
                    self.z_calib = resoz
                    resoz = str(int(resoz * 1e9))
                
                zoom_column_item = QtImport.QTableWidgetItem(str(current_pos))
                y_column_item = QtImport.QTableWidgetItem(resoy)
                z_column_item = QtImport.QTableWidgetItem(resoz)

                self.ui_widgets_manager.beam_positions_table.setItem(self.curr_idx, 0, zoom_column_item)
                self.ui_widgets_manager.beam_positions_table.setItem(self.curr_idx, 1, y_column_item)
                self.ui_widgets_manager.beam_positions_table.setItem(self.curr_idx, 2, z_column_item)
                
            else:
                self.y_calib = None
                self.z_calib = None
        else:
            self.y_calib = None
            self.z_calib = None

        # self.emit(qt.PYSIGNAL("ChangePixelCalibration"),
        #           (self.y_calib, self.z_calib))
    
    def zoom_state_changed(self):
        pass

    def save_calibration(self):
        """
        """
        if self.zoom_motor_hwobj is not None:
            currentPos = self.zoom_motor_hwobj.getPosition()
            self.zoom_motor_hwobj.setPositionKeyValue(currentPos, "resox", str(self.y_calib))
            self.zoom_motor_hwobj.setPositionKeyValue(currentPos, "resoy", str(self.z_calib))
        else:
            print(f"CameraCalibrationBrick--ARG--zoom_motor_hwobj is None")
                
    def start_new_calibration(self):
        """
        Doc
        """

        hor_motor_delta = float(self.ui_widgets_manager.delta_y_textbox.text())
        ver_motor_delta = float(self.ui_widgets_manager.delta_z_textbox.text())
        
        print(f"CameraCalibrationBrick--start_new_calibration")
        if HWR.beamline.sample_view is not None:
            HWR.beamline.sample_view.start_calibration()
            if HWR.beamline.diffractometer is not None:
                HWR.beamline.diffractometer.set_calibration_parameters(
                    hor_motor_delta,
                    ver_motor_delta
                )
                print(f"CameraCalibrationBrick--HWR.beamline.diffractometer is not None {hor_motor_delta} - {ver_motor_delta} ")

                HWR.beamline.diffractometer.start_manual_calibration()
            
            
                
        # if self.calibration == 0:

        #     if self.drawingMgr is not None:
        #         self.calibration = 1
        #         self.calibButton.setText("Cancel Calibration")

        #         self.drawingMgr.startDrawing()

        # elif self.calibration == 1:
        #     self.calibration = 0
        #     self.calibButton.setText("Start New Calibration")
        #     self.drawingMgr.stopDrawing()
        #     self.drawingMgr.hide()

        # elif self.calibration == 2:
        #     self.disconnect(self.vmot, qt.PYSIGNAL("moveDone"),
        #                     self.moveFinished)
        #     self.disconnect(self.hmot, qt.PYSIGNAL("moveDone"),
        #                     self.moveFinished)
        #     self.hmot.stop()
        #     self.vmot.stop()
        #     self.calibration = 0
        #     self.calibButton.setText("Start New Calibration")
        #     self.drawingMgr.stopDrawing()
        #     self.drawingMgr.hide()

    def diffractometer_manual_calibration_done(self, two_calibration_points):
        """
        Descript. :
        """
        print(f"CameraCalibrationBrick--diffractometer_manual_calibration_done - {two_calibration_points}")

        HWR.beamline.sample_view.stop_calibration()
        
        msgstr = f"Calibration : {two_calibration_points}"

        QtImport.QMessageBox.information(
                    self,
                    "Calibration ended",
                    msgstr,
                    QtImport.QMessageBox.Ok,
                )

        # msg = QtImport.QMessageBox.information()
        
        # msg.setText(msgstr)
        # msg.setWindowTitle("Calibration ended")
        # msg.setStandardButtons(QMessageBox.Ok)
        # retval = msg.exec_()

    def clear_table(self):
        """
        Adapt
        """
        #table = self.ui_widgets_manager.findChild(QtI
        # mport.QTableWidget, "aligment_table")
        table = self.ui_widgets_manager.aligment_table
        table.clearContents()
            