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

This brick displays and saves for different zoom value a beam position.

It displays information from:
* xml file ( at origin, called multiple-positions )
    * For each zoom motor position, user can see and edit:
        * Beam position values
IMPORTANT!! : this data is delivered by the MultiplePositions HWRObject:
this object handles (load/edit/save) and delivers to different bricks to be displayed/edited like
CameraBeamBrick / CameraBeamBrick

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
import os

from gui.utils import Icons, Colors, QtImport
from gui.BaseComponents import BaseWidget
from HardwareRepository import HardwareRepository as HWR

try:
    from xml.etree import cElementTree  # python2.5
except ImportError:
    import cElementTree

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "ESRF"

class ESRFCameraBeamBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # variables -----------------------------------------------------------

        self.current_beam_position = None
        #self.beam_position_dict = {} # { "position_name" : (pos_x, pos_y)} pixels
        self.current_zoom_pos_name = None
        self.current_zoom_idx = -1
        self.multipos_hwobj_xml_path = None

        # Hardware objects ----------------------------------------------------
        self.multipos_hwobj = None
        
        # Internal values -----------------------------------------------------
        self.table_created = False
        # Properties ----------------------------------------------------------
        self.add_property("zoom", "string", "")
        
        # Signals ------------------------------------------------------------
        #self.define_signal("ChangeBeamPosition", ())
        
        # Slots ---------------------------------------------------------------
        #self.define_slot("getBeamPosition", ())
        #self.define_slot("beamPositionChanged", ())
        self.define_slot("setBrickEnabled", ())
        
        # Graphic elements ----------------------------------------------------
        self.main_groupbox = QtImport.QGroupBox("Beam Position", self)
        self.ui_widgets_manager = QtImport.load_ui_file("camera_beam_brick.ui")

        # Size policy --------------------------------
        self.ui_widgets_manager.beam_positions_table.setSizePolicy(
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
       
        self.ui_widgets_manager.save_current_beam_pos_pushbutton.clicked.connect(
            self.save_beam_position
        )

        # Other hardware object connections --------------------------

        # Wanted to connect directly HWR.beamline.sample_view signal to 
        # self.multipos_hwobj but sample_view is not created by the time
        # self.multipos_hwobj.init() is executed : create a pass by way
        # not very elegant... 

        if HWR.beamline.sample_view is not None:
            self.connect(HWR.beamline.sample_view,
                        "beam_position_data_changed",
                        self.beam_position_data_changed
            )
        else:
            print(f"CameraBeamBrick : HWR.beamline.sample_view NONE")

        # if HWR.beamline.beam is not None:
        #     self.beam_position = HWR.beamline.beam.get_beam_position_on_screen()
        #     self.connect(
        #         HWR.beamline.beam, "beamPosChanged", self.beam_position_edited
        #     )
        #     #self.beam_position_changed(HWR.beamline.beam.get_beam_position_on_screen())
        # else:
        #     logging.getLogger("HWR").error(
        #         "GraphicsManager: BeamInfo hwobj not defined"
        #     )

        #self.load_beam_position_dict()

    # def load_beam_position_dict(self):
    #     """
    #     # { "position_name" : (beam_pos_x, beam_pos_y)} meters/pixel
    #     """
    #     if self.multipos_hwobj is not None:
    #         positions = self.multipos_hwobj.get_positions_names_list()
    #         for i, position in enumerate(positions):
    #         # for i,  in range(pos):
    #             aux = self.multipos_hwobj.get_position_key_value(position, "beam_pos_x")
    #             if aux is None:
    #                 aux = 0
    #             beam_pos_x = abs(int(aux))
    #             aux = self.multipos_hwobj.get_position_key_value(position, "beam_pos_y")
    #             if aux is None:
    #                 aux = 0
    #             beam_pos_y = abs(int(aux))
                
    #             self.beam_position_dict[position] = (beam_pos_x, beam_pos_y)   
    #     print(f"################ cameraCalibBrick beam_position_dict {self.beam_position_dict}")
    def beam_position_data_changed(self, new_beam_data):
        
        dict_elem = self.multipos_hwobj.get_current_position()

        dict_elem["beam_pos_x"] = new_beam_data[0]
        dict_elem["beam_pos_y"] = new_beam_data[1]

        self.multipos_hwobj.edit_data(dict_elem, None, 0)

    def property_changed(self, property_name, old_value, new_value):
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

            self.multipos_hwobj = self.get_hardware_object(new_value)

            if new_value.startswith("/"):
                    new_value = new_value[1:]

            self.multipos_file_xml_path = os.path.join(
                HWR.getHardwareRepositoryConfigPath(),
                new_value + ".xml")

            if self.multipos_hwobj is not None:
                # if new_value.startswith("/"):
                #     new_value = new_value[1:]
                # print(f"################ cameraCalibBrick property_changed - new full path {new_value}")

                # self.multipos_hwobj_xml_path = os.path.join(
                #     HWR.getHardwareRepositoryConfigPath(),
                #     new_value + ".xml")
                # print(f"################ cameraCalibBrick property_changed - new full path {self.multipos_hwobj_xml_path}")

                #self.load_beam_position_dict()
                # self.connect(self.multipos_hwobj, "predefinedPositionChanged",
                #                 self.zoom_changed)
                # self.connect(self.multipos_hwobj, "no_position",
                #                 self.zoom_changed)

                self.connect(self.multipos_hwobj, "beam_pos_cal_data_changed",
                                self.beam_cal_pos_data_changed)
                self.connect(self.multipos_hwobj, "beam_pos_cal_data_saved",
                                self.beam_cal_pos_data_saved)
                self.connect(self.multipos_hwobj, "beam_pos_cal_data_cancelled",
                                self.beam_cal_pos_data_cancelled)

                # self.zoom_changed(self.multipos_hwobj.get_value())
            self.init_interface()
        
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

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
        self.init_interface()
        
    def beam_cal_pos_data_changed(self, who_changed):
        # TODO : identify changed data and set cell background to yellow
        self.init_interface()

        pos_name = self.multipos_hwobj.get_value()
        table = self.ui_widgets_manager.beam_positions_table

        print(f"################ cameraBeamBrick beam_cal_pos_data_changed - PRINT BACKGROUND {pos_name} ")
        for index_row in range(table.rowCount()):
            print(f"################ cameraBeamBrick beam_cal_pos_data_changed - PRINT BACKGROUND index_row {index_row} ")
            if table.item(index_row, 0).text() == pos_name:
                table.item(index_row, 1).setBackground(QtImport.QColor(QtImport.Qt.yellow))
                table.item(index_row, 2).setBackground(QtImport.QColor(QtImport.Qt.yellow))
                
    def init_interface(self):
        tmp_dict = self.multipos_hwobj.get_positions()

        if tmp_dict:
            if not self.table_created:
                # create table items for first and only time
                
                self.ui_widgets_manager.beam_positions_table.setRowCount(len(tmp_dict))

                for row in range(len(tmp_dict)):
                    for col in range(3):
                        tmp_item = QtImport.QTableWidgetItem()
                        tmp_item.setFlags(tmp_item.flags() ^ QtImport.Qt.ItemIsEditable)
                        self.ui_widgets_manager.beam_positions_table.setItem(
                            row,
                            col,
                            tmp_item
                        )
                self.table_created = True

            print(f"################ cameraBeamBrick init_interface - {len(tmp_dict)} ")
            table = self.ui_widgets_manager.beam_positions_table

            for i, (position, position_dict) in enumerate(tmp_dict.items()):
                beam_pos_x = position_dict["beam_pos_x"]
                beam_pos_y = position_dict["beam_pos_y"]
            
                table.item(i, 0).setText(str(position))
                table.item(i, 1).setText(str(beam_pos_x))
                table.item(i, 2).setText(str(beam_pos_y))

    # def get_zoom_index(self, position_to_find):
    #     if self.multipos_hwobj is not None:
    #         positions = self.multipos_hwobj.get_positions_names_list()
    #         for i, position in enumerate(positions):
    #             if position_to_find == position:
    #                 return(i)
    #         return(-1)

    # def zoom_changed(self, name):
    #     if name is None:
    #         logging.getLogger("HWR").error("Multiple Position motor in no_position state")
    #         return
    #     if self.multipos_hwobj is not None:
    #         self.current_zoom_pos_name = name # self.multipos_hwobj.get_value()
    #         self.current_zoom_idx = self.get_zoom_index(name)
    #         print(f"################ cameraBeamBrick zoom_changed current_zoom_pos_name : {self.current_zoom_pos_name} + current_zoom_idx : {self.current_zoom_idx}")        
    #         if self.current_zoom_idx != -1:
    #             self.current_beam_position = self.beam_position_dict[name]
    #             print(f"################ cameraBeamBrick zoom_changed beampos : {self.current_beam_position} + zoom pos : {self.current_zoom_pos_name}")
    #             if self.ui_widgets_manager.beam_positions_table.itemAt(self.current_zoom_idx, 1):
    #                 self.ui_widgets_manager.beam_positions_table.item(self.current_zoom_idx, 1).setText(str(int(self.current_beam_position[0])))
    #                 self.ui_widgets_manager.beam_positions_table.item(self.current_zoom_idx, 2).setText(str(int(self.current_beam_position[1])))
    #             else:
    #                 print(f"################ cameraBeamBrick zoom_changed TABLE NOT INITIALIZED")
                
    # def beam_position_changed(self,beam_x_y):
    #     """
    #         beam_x_y (tuple): Position (x, y) [pixel]
    #     """
    #     #update current_zoom_idx
    #     self.current_zoom_idx = self.get_zoom_index(self.multipos_hwobj.get_value())
    #     print(f"################ cameraBeamBrick beam_position_changed beampos : {beam_x_y} + zoom pos : {self.current_zoom_pos_name} - current_zoom_idx : {self.current_zoom_idx}")
    #     self.current_beam_position = beam_x_y

    #     self.ui_widgets_manager.beam_positions_table.item(
    #         self.current_zoom_idx, 1).setText(str(int(beam_x_y[0]))
    #     )
    #     self.ui_widgets_manager.beam_positions_table.item(
    #         self.current_zoom_idx, 2).setText(str(int(beam_x_y[1]))
    #     )

    #     self.ui_widgets_manager.beam_positions_table.item(
    #         self.current_zoom_idx, 1).setBackground(
    #             QtImport.QColor(QtImport.Qt.yellow
    #         )
    #     )

    #     self.ui_widgets_manager.beam_positions_table.item(
    #         self.current_zoom_idx, 2).setBackground(
    #             QtImport.QColor(QtImport.Qt.yellow
    #         )
    #     )

    def clean_cells_background(self):
        """
        clean cells background color
        """
        table = self.ui_widgets_manager.beam_positions_table

        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                table.item(row, col).setData(QtImport.Qt.BackgroundRole, None)

    def save_beam_position(self):
        """
        send signal to self.multipos_hwobj to save data to file
        clean cells background color
        """
        if self.multipos_hwobj is not None:
            self.multipos_hwobj.save_data_to_file(self.multipos_file_xml_path)

        self.clean_cells_background()
        
        
        # """
        # Doc
        # """
        # if self.multipos_hwobj is not None:
        #     # TODO : change how data is handled in MultiposHwrObject
        #     # I think best: to record on xml and reload data on hwr_obj 
        #     # to reuse self["positions"]
        #     current_pos = self.multipos_hwobj.get_value()
            
        #     self.multipos_hwobj.set_position_key_value(
        #         current_pos,
        #         'beamx',
        #         self.current_beam_position[0]
        #         )

        #     self.multipos_hwobj.set_position_key_value(
        #         current_pos,
        #         'beamy',
        #         self.current_beam_position[1]
        #         )

        #     #open xml file
        #     xml_file_tree = cElementTree.parse(self.multipos_hwobj_xml_path)

        #     xml_tree = xml_file_tree.getroot()
        #     positions = xml_tree.find("positions")
            
        #     pos_list = positions.findall("position")
        #     # pdb.set_trace()

        #     for pos in pos_list:
        #         if pos.find("name").text == current_pos:
        #             if pos.find('beamx') is not None:
        #                 pos.find('beamx').text = str(self.current_beam_position[0])
        #             if pos.find('beamy') is not None:
        #                 pos.find('beamy').text = str(self.current_beam_position[1])
            
        #     xml_file_tree.write(self.multipos_hwobj_xml_path)

        # else:
        #     print(f"CameraCalibrationBrick--ARG--multipos_hwobj is None")
               
    
    def clear_table(self):
        """
        Adapt
        """
        #table = self.ui_widgets_manager.findChild(QtI
        # mport.QTableWidget, "aligment_table")
        self.ui_widgets_manager.beam_positions_table.clearContents()
            