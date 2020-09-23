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
import os

from gui.utils import Icons, Colors, QtImport
from gui.BaseComponents import BaseWidget

from HardwareRepository import HardwareRepository as HWR
from HardwareRepository.HardwareObjects import sample_centring

try:
    from xml.etree import cElementTree  # python2.5
except ImportError:
    import cElementTree


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "ESRF"

class ESRFCameraCalibrationBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # variables -----------------------------------------------------------

        self.y_calib = None # metres/pixel
        self.z_calib = None # metres/pixel
        self.calibration = 0
        self.drawing = None
        self.drawing_mgr = None
        self.current_calibration_procedure = None
        #self.calibration_dict = {} # { "position_name" : (resox, resoy)} metres/pixel
        self.current_zoom_pos_name = None
        #self.current_zoom_idx = -1
        self.multipos_file_xml_path = None
        self.table_created = False

        # Hardware objects ----------------------------------------------------
        self.multipos_hwobj = None
        self.h_motor_hwobj = None
        self.v_motor_hwobj = None

        # Properties ----------------------------------------------------------
        self.add_property("zoom", "string", "")
        self.add_property("vertical motor", "string", "")
        self.add_property("horizontal motor", "string", "")
        
        # Signals ------------------------------------------------------------
        self.define_signal("getBeamPosition", ())
        
        # Graphic elements ----------------------------------------------------
        self.main_groupbox = QtImport.QGroupBox("Pixel Size Calibration", self)
        self.ui_widgets_manager = QtImport.load_ui_file("camera_calibration.ui")

        # Size policy --------------------------------
        self.ui_widgets_manager.calibration_table.setSizePolicy(
            QtImport.QSizePolicy.Minimum,
            QtImport.QSizePolicy.Minimum,
        )

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
            self.save_new_calibration_value
        )

        self.ui_widgets_manager.start_new_calibration_pushbutton.clicked.connect(
            self.start_new_calibration
        )

        self.ui_widgets_manager.cancel_calibration_pushbutton.clicked.connect(
            self.cancel_calibration
        )

        # Other hardware object connections --------------------------
        self.connect(
            HWR.beamline.diffractometer,
            "new_calibration_done",
            self.diffractometer_manual_calibration_done,
        )

        # self.load_calibration_dict()
    
    # def load_calibration_dict(self):
    #     """
    #     # { "position_name" : (resox, resoy)} meters/pixel
    #     """
    #     if self.multipos_hwobj is not None:
    #         positions = self.multipos_hwobj.get_positions_names_list()
    #         for i, position in enumerate(positions):
    #         # for i,  in range(pos):
    #             aux = self.multipos_hwobj.get_position_key_value(position, "resox")
    #             if aux is None:
    #                 aux = 1
    #             resox = abs(float(aux))
    #             aux = self.multipos_hwobj.get_position_key_value(position, "resoy")
    #             if aux is None:
    #                 aux = 1
    #             resoy = abs(float(aux))
                
    #             self.calibration_dict[position] = (resox, resoy)   
    #     print(f"################ cameraCalibBrick load_calibration_dict {self.calibration_dict}")
        

    def property_changed(self, property_name, old_value, new_value):
        print(f"cameraCalibBrick property_changed {new_value}")
        if property_name == "zoom":
            
            if self.multipos_hwobj is not None:
                # self.disconnect(self.multipos_hwobj, "predefinedPositionChanged",
                #                 self.zoom_changed)
                # self.disconnect(self.multipos_hwobj, "no_position",
                #                 self.zoom_changed)
                self.disconnect(self.multipos_hwobj, "beam_pos_cal_data_changed",
                                self.beam_cal_pos_data_changed)
                self.disconnect(self.multipos_hwobj, "beam_pos_cal_data_saved",
                                self.beam_cal_pos_data_saved)
                self.disconnect(self.multipos_hwobj, "beam_pos_cal_data_cancelled",
                                self.beam_cal_pos_data_cancelled)

            if new_value is not None:
                self.multipos_hwobj = self.get_hardware_object(new_value)
                if new_value.startswith("/"):
                    new_value = new_value[1:]
                self.multipos_file_xml_path = os.path.join(
                    HWR.getHardwareRepositoryConfigPath(),
                    new_value + ".xml"
                )
                

            # if self.multipos_hwobj is None:
            #     # first time motor is set
            #     try:
            #         step = float(self.default_step)
            #     except BaseException:
            #         try:
            #             step = self.multipos_hwobj.GUIstep
            #         except BaseException:
            #             step = 1.0
            #     self.set_line_step(step)

            if self.multipos_hwobj is not None:
                # self.load_calibration_dict()
                # self.connect(self.multipos_hwobj, "predefinedPositionChanged",
                #             self.zoom_changed)
                # self.connect(self.multipos_hwobj, "no_position",
                #             self.zoom_changed)
                # self.zoom_changed(self.multipos_hwobj.get_value()).

                self.connect(self.multipos_hwobj, "beam_pos_cal_data_changed",
                                self.beam_cal_pos_data_changed)
                self.connect(self.multipos_hwobj, "beam_pos_cal_data_saved",
                                self.beam_cal_pos_data_saved)
                self.connect(self.multipos_hwobj, "beam_pos_cal_data_cancelled",
                                self.beam_cal_pos_data_cancelled)

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
        
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def beam_cal_pos_data_changed(self, who_changed, new_data_dict):
        # TODO : identify changed data and set cell background to yellow
        print(f"################ cameraCalibBrick beam_cal_pos_data_changed who_changed {who_changed}")
        if who_changed == 0:
            return

        print(f"################ cameraCalibBrick beam_cal_pos_data_changed update_gui")
        self.update_gui()

        if new_data_dict:
            pos_name = new_data_dict["zoom_tag"]
        else:
            pos_name = self.multipos_hwobj.get_value()
        
        table = self.ui_widgets_manager.calibration_table

        print(f"################ cameraCalibBrick beam_cal_pos_data_changed pos_name {pos_name}")
        for index_row in range(table.rowCount()):
            print(f"################ cameraCalibBrick beam_cal_pos_data_changed index_row {index_row} - {table.rowCount()}")
            if table.item(index_row, 0).text() == pos_name:
                print(f"################ cameraCalibBrick beam_cal_pos_data_changed pos_name {pos_name}")
                table.item(index_row, 1).setBackground(QtImport.QColor(QtImport.Qt.yellow))
                table.item(index_row, 2).setBackground(QtImport.QColor(QtImport.Qt.yellow))
            
    def beam_cal_pos_data_saved(self):
        """
        data saved: clean cell background
        """
        self.clean_cells_background()
    def beam_cal_pos_data_cancelled(self):
        """
        data cancelled:
        clean cell background
        reload data from hardware object
        """
        self.clean_cells_background()
        self.update_gui()

    def update_gui(self):
        
        tmp_dict = self.multipos_hwobj.get_positions()
        #print(f"################ cameraCalibBrick update_gui {self.calibration_dict}")
        if tmp_dict:

            if not self.table_created:
                # create table items for first and only time
                
                self.ui_widgets_manager.calibration_table.setRowCount(len(tmp_dict))

                for row in range(len(tmp_dict)):
                    for col in range(3):
                        tmp_item = QtImport.QTableWidgetItem()
                        tmp_item.setFlags(tmp_item.flags() ^ QtImport.Qt.ItemIsEditable)
                        self.ui_widgets_manager.calibration_table.setItem(
                            row,
                            col,
                            tmp_item
                        )
                self.table_created = True

            table = self.ui_widgets_manager.calibration_table
            for i, (position, position_dict) in enumerate(tmp_dict.items()):
                
                if position_dict["cal_x"] == 1:
                    y_calib = "Not defined"
                else:
                    y_calib = str(abs(int(position_dict["cal_x"])))
                if position_dict["cal_y"] == 1:
                    z_calib = "Not defined"
                else:
                    z_calib = str(abs(int(position_dict["cal_y"])))
                """
                resolution are displayed in nanometer/pixel and saved in metre/pixel
                """
                table.item(i, 0).setText(str(position))
                table.item(i, 1).setText(y_calib)
                table.item(i, 2).setText(z_calib)

    # def get_zoom_index(self, position_to_find):
    #     if self.multipos_hwobj is not None:
    #         positions = self.multipos_hwobj.get_positions_names_list()
    #         for i, position in enumerate(positions):
    #             if position_to_find == position:
    #                 return(i)
    #         return(-1)

    # def zoom_changed(self, current_pos_name):
    #     if current_pos_name is None:
    #         logging.getLogger("HWR").error("Multiple Position motor in no_position state")
    #         return
            
    #     #print(f"################ cameraCalibBrick zoom_changed {self.calibration_dict}")
    #     if self.multipos_hwobj is not None:
    #         # current_pos = self.multipos_hwobj.get_value()
    #         self.current_zoom_idx = self.get_zoom_index(current_pos_name)
    #         self.current_zoom_pos_name = current_pos_name

    #         if len(self.ui_widgets_manager.calibration_table.selectedItems()) != 0:
    #             self.ui_widgets_manager.calibration_table.clearSelection()
                
    #         if self.current_zoom_idx != -1:
    #             new_calibration = self.calibration_dict[current_pos_name]
    #             #print(f"################ cameraCalibBrick zoom_changed {new_calibration} + {current_pos_name}")

    #             if new_calibration[0] == 1:
    #                 self.y_calib = None
    #             else:
    #                 self.y_calib = new_calibration[0]

    #             if new_calibration[1] == 1:
    #                 self.z_calib = None
    #             else:
    #                 self.z_calib = new_calibration[1]
                                
    #         else:
    #             self.y_calib = None
    #             self.z_calib = None
    #     else:
    #         self.y_calib = None
    #         self.z_calib = None

        #print(f"################ cameraCalibBrick zoom_changed {self.y_calib} + {self.z_calib}")

        # self.emit(qt.PYSIGNAL("ChangePixelCalibration"),
        #           (self.y_calib, self.z_calib))
    
    def zoom_state_changed(self):
        pass

    def clean_cells_background(self):
        """
        clean cells background color
        """
        table = self.ui_widgets_manager.calibration_table

        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                table.item(row, col).setData(QtImport.Qt.BackgroundRole, None)

    def save_new_calibration_value(self):
        """
        send signal to self.multipos_hwobj to save data to file
        clean cells background color
        """

        if self.multipos_hwobj is not None:
            self.multipos_hwobj.save_data_to_file(self.multipos_file_xml_path)

        self.clean_cells_background()

        # 'save' new data in hwrobjec
        # TODO : change how data is handled in MultiposHwrObject
        # I think best: to record on xml and reload data on hwr_obj 
        # to reuse self["positions"]

        # self.y_calib = float(new_calibration[0]/1000.0) # metres/pixel
        # self.z_calib = float(new_calibration[1]/1000.0) # metres/pixel

        # current_pos = self.multipos_hwobj.get_value()
            
        # self.multipos_hwobj.set_position_key_value(
        #     current_pos,
        #     'resox',
        #     self.y_calib
        #     )

        # self.multipos_hwobj.set_position_key_value(
        #     current_pos,
        #     'resoy',
        #     self.z_calib
        #     )

        # # save on xml file
        # xml_file_tree = cElementTree.parse(self.multipos_hwobj_xml_path)

        # xml_tree = xml_file_tree.getroot()
        # positions = xml_tree.find("positions")
        
        # pos_list = positions.findall("position")
        # # pdb.set_trace()

        # for pos in pos_list:
        #     if pos.find("name").text == current_pos:
        #         if pos.find('resox') is not None:
        #             pos.find('resox').text = str(self.y_calib)
        #         if pos.find('resoy') is not None:
        #             pos.find('resoy').text = str(self.z_calib)
        
        # xml_file_tree.write(self.multipos_hwobj_xml_path)

    def cancel_calibration(self):
        """
        Doc
        """
        print(f"CameraCalibrationBrick--cancel calibration")
        HWR.beamline.diffractometer.cancel_manual_calibration()

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

    def diffractometer_manual_calibration_done(self, two_calibration_points):
        """
        Descript. :
        """
        print(f"CameraCalibrationBrick--diffractometer_manual_calibration_done - {two_calibration_points}")

        HWR.beamline.sample_view.stop_calibration()
        
        delta_x_pixels = abs(two_calibration_points[0][0] - two_calibration_points[1][0])
        delta_y_pixels = abs(two_calibration_points[0][1] - two_calibration_points[1][1])

        hor_motor_delta = float(self.ui_widgets_manager.delta_y_textbox.text()) # milimeters
        ver_motor_delta = float(self.ui_widgets_manager.delta_z_textbox.text())

        print(f"CameraCalibrationBrick--diffractometer_manual_calibration_done - {delta_x_pixels} - {delta_y_pixels} - {hor_motor_delta} - {ver_motor_delta}")
        print(f"CameraCalibrationBrick--diffractometer_manual_calibration_done - {float(hor_motor_delta/delta_x_pixels)} - {float(ver_motor_delta/delta_y_pixels)}")


        self.y_calib = float(hor_motor_delta/delta_x_pixels) * 1e-3 # metres/pixel
        self.z_calib = float(ver_motor_delta/delta_y_pixels) * 1e-3

        self.multipos_hwobj.calibration_data_changed(
            (self.y_calib * 1e9, self.z_calib * 1e9)
        )

        # current_pos_name = self.multipos_hwobj.get_value()
        # table = self.ui_widgets_manager.calibration_table
        # #display data in table
        # for row_index in range(table.rowCount()):
        #     if table.item(row_index, 0).text() == current_pos_name:
        #         table.item(row_index, 1).setText(str(int(self.y_calib * 1e9)))
        #         table.item(row_index, 1).setBackground(Colors.LIGHT_YELLOW)
        #         table.item(row_index, 2).setText(str(int(self.z_calib * 1e9)))
        #         table.item(row_index, 2).setBackground(Colors.LIGHT_YELLOW)

        
        
        # msgstr = f"Calculated new calibration : {y_calib} , {z_calib} ( nm/pixel )"
        # "for zoom position {self.current_zoom_pos_name}."
        # "Would you like to keep it??"
        # "To save data to xml file, click on 'Save Calibration' button"

        # keep_new_calib = QtImport.QMessageBox.question(
        #             self,
        #             "Keep new calibration ?",
        #             msgstr,
        #             QtImport.QMessageBox.Yes | 
        #             QtImport.QMessageBox.No,
        #         )
        # if keep_new_calib == QtImport.QMessageBox.Yes:
        #     print(f" answer yes")
        #     self.set_new_calibration_value((y_calib,z_calib))
        # else:
        #     print(f" answer no")
        #     return
        # # return ( two_calibration_points[0] )

    def clear_table(self):
        """
        Adapt
        """
        #table = self.ui_widgets_manager.findChild(QtI
        # mport.QTableWidget, "aligment_table")
        table = self.ui_widgets_manager.aligment_table
        table.clearContents()
            
