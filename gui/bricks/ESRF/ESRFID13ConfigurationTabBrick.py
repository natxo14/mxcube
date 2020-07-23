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
ESRF ID13 ConfigurationTab

[Description]

This brick displays configuation information related to ID13 EH2/EH3 beamlines at ESRF.
It displays information from:
* xml file ( at origin, called multiple-positions )

    * For each zoom motor position, user can see and edit:
        * Beam position values
        * Camera calibration ( nm / pixel )
        * ligth emiting device value
    * A list of editable 'tags' of different 'operation mode' (ex: signal, background, empty)
        this operation mode will be lately used by ESRFDataExportBrick to tag exported data

* Bliss/ESRF data policy : data saving paths of current experiment

[Properties]

xml file

[Signals]

graphic_data_edited - emitted when any of the data has been edited (not yet saved)
params : freshly edited graphic data as dict

TODO: maybe split in beam_position_changed / calibration_changed ??

graphic_data_saved - emitted when data is saved in xml file

operation_modes_edited - emitted when operation mode list edited (not yet saved)

operation_modes_saved - emitted when operation mode list is saved in xml file

[Slots]

beamPositionChanged - y_beam, z_beam, zoom_pos 
                                    - slot which should be connected to all
                                     client able to change beam position.
                                     
calibration_changed - y_res, z_res, zoom_pos 
                                    - slot which should be connected to all
                                     client able to change calibration.
                                     

setBrickEnabled - isEnabled - slot to call to disable the brick (expert mode for example).

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

class ESRFID13ConfigurationTabBrick(BaseWidget):
 
    graphic_data_edited = QtImport.pyqtSignal(dict)
    graphic_data_saved = QtImport.pyqtSignal()
    operation_modes_edited = QtImport.pyqtSignal(list)
    operation_modes_saved = QtImport.pyqtSignal()
    
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # variables -----------------------------------------------------------

        self.zoom_positions_dict = {}
        #{ "position_name" : { "pos_x" : val, int - pixels
        #                      "pos_y" : val, int - pixels
        #                      "cal_x" : val, int - nm
        #                      "cal_y" : val, int - nm
        #                      "ligth" : val,
        #                     },
        #}

        self.list_of_operational_modes = []

        self.current_beam_position = None
        self.current_zoom_pos_name = None
        self.current_zoom_idx = -1
        self.multipos_file_xml_path = None
        self.bliss_session_list = None
        self.bliss_config = static.get_config()

        # Hardware objects ----------------------------------------------------
        
        # Internal values -----------------------------------------------------
        
        # Properties ----------------------------------------------------------
        self.add_property("configfile", "string", "/multiple-positions")
        
        # Signals ------------------------------------------------------------
        self.define_signal("graphic_data_edited", ())
        self.define_signal("graphic_data_saved", ())

        self.define_signal("operation_modes_edited", ())
        self.define_signal("operation_modes_saved", ())
        
        # Slots ---------------------------------------------------------------
        self.define_slot("getBeamPosition", ())
        self.define_slot("beamPositionChanged", ())
        self.define_slot("setBrickEnabled", ())
        
        # Graphic elements ----------------------------------------------------
        self.main_groupbox = QtImport.QGroupBox("Beam Configuration", self)
        self.ui_widgets_manager = QtImport.load_ui_file("esrf_id13_configuration_widget.ui")

        # Size policy --------------------------------
        self.ui_widgets_manager.configuration_table.setSizePolicy(
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
       
        self.ui_widgets_manager.save_table_changes.clicked.connect(
            self.save_table_changes
        )

        self.ui_widgets_manager.cancel_table_changes.clicked.connect(
            self.cancel_table_changes
        )

        self.ui_widgets_manager.reload_data_policy.clicked.connect(
            self.display_data_policy
        )

        self.ui_widgets_manager.bliss_session_combo_box.currentIndexChanged.connect(
            self.display_data_policy
        )

        self.ui_widgets_manager.configuration_table.itemChanged.connect(
            self.configuration_table_item_changed
        )

        self.ui_widgets_manager.add_label_button.clicked.connect(
            self.add_op_mode_to_list
        )

        self.ui_widgets_manager.delete_label_button.clicked.connect(
            self.delete_op_mode_from_list
        )

        self.ui_widgets_manager.save_labels_button.clicked.connect(
            self.save_op_mode_list
        )

        self.ui_widgets_manager.label_list.currentRowChanged.connect(
            self.label_list_selection_changed
        )


        # Other hardware object connections --------------------------
        if HWR.beamline.beam is not None:
            self.beam_position = HWR.beamline.beam.get_beam_position_on_screen()
            self.connect(
                HWR.beamline.beam, "beamPosChanged", self.beam_position_changed
            )
            #self.beam_position_changed(HWR.beamline.beam.get_beam_position_on_screen())
        else:
            logging.getLogger("HWR").error(
                "GraphicsManager: BeamInfo hwobj not defined"
            )

        self.init_interface()
    
    def configuration_table_item_changed(self, item):
        item.setBackground(QtImport.QColor(QtImport.Qt.yellow))

    def load_zoom_positions_dict(self):
        """
        Parse xml file and load dict :

        { "position_name" : { "pos_x" : val,int - pixels  
                             "pos_y" : val,int - pixels
                             "cal_x" : val,int - nm
                             "cal_y" : val,int - nm
                             "light" : val,
                            },
        }
        """
        output_dict = {}
        xml_file_tree = cElementTree.parse(self.multipos_file_xml_path)

        xml_tree = xml_file_tree.getroot()
        positions = xml_tree.find("positions")

        pos_list = positions.findall("position")
        
        for pos in pos_list:
            
            if pos.find("beamx") is not None:
                pos_x = self.from_text_to_int(pos.find("beamx").text)
            else:
                pos_x = 0
            if pos.find("beamy") is not None:
                pos_y = self.from_text_to_int(pos.find("beamy").text)
            else:
                pos_y = 0
            if pos.find("resox") is not None:
                cal_x = self.from_text_to_int(pos.find("resox").text, 1e9)
            else:
                cal_x = 0
            if pos.find("resoy") is not None:
                cal_y = self.from_text_to_int(pos.find("resoy").text, 1e9)
            else:
                cal_y = 0
            
            if pos.find("light") is not None:
                light_val = self.from_text_to_int(pos.find("light").text, 1e9)
            else:
                light_val = 0
            
            dict_elem = {"pos_x" : pos_x,
                        "pos_y" : pos_y,
                        "cal_x" : cal_x,
                        "cal_y" : cal_y,
                        "light" : light_val,
            }
            output_dict[pos.find('name').text] = dict_elem
            
        self.zoom_positions_dict = copy.deepcopy(output_dict)

    def load_list_of_operational_modes(self):
        """
        Parse xml file and load list of operational modes :

        'tag0', 'tag1', ...
        """
        xml_file_tree = cElementTree.parse(self.multipos_file_xml_path)

        xml_tree = xml_file_tree.getroot()
        mode_list = []
        if xml_tree.find("operational_modes") is not None:
            #print(f"xml_tree.find(operational_modes) is not None:")
            mode_list = xml_tree.find("operational_modes").text

        #print(f"list_of_operational_modes :mode_list {mode_list} - {type(mode_list)}")
        self.list_of_operational_modes = eval(mode_list)
        #print(f"list_of_operational_modes :mode_list {self.list_of_operational_modes} - {type(self.list_of_operational_modes)} - {type(self.list_of_operational_modes[0])}")
        
    def from_text_to_int(self, input_str, factor=1):
        if input_str is None:
            return 0
        return abs(int(float(input_str) * factor))
    
    def property_changed(self, property_name, old_value, new_value):
        if property_name == "configfile":
            print(f"################ cameraCalibBrick property_name  new_value {new_value}")
            if new_value.startswith("/"):
                    new_value = new_value[1:]

            self.multipos_file_xml_path = os.path.join(
                HWR.getHardwareRepositoryConfigPath(),
                new_value + ".xml")
            print(f"################ CONFIGTABBRICK property_changed - new full path {self.multipos_file_xml_path}")
            self.load_zoom_positions_dict()
            self.load_list_of_operational_modes()
            
            self.init_interface()

        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def fill_op_modes_list(self):
        if self.list_of_operational_modes is not None:
            self.ui_widgets_manager.label_list.clear()

            for tag_text in self.list_of_operational_modes:
                self.ui_widgets_manager.label_list.addItem(tag_text)


    def fill_config_table(self):
        if self.zoom_positions_dict is not None:

            self.clear_table()
            self.ui_widgets_manager.configuration_table.setRowCount(len(self.zoom_positions_dict))
            self.ui_widgets_manager.configuration_table.itemChanged.disconnect(
                self.configuration_table_item_changed
            )

            for i, (position, position_dict_elem) in enumerate(self.zoom_positions_dict.items()):
                
                zoom_position_item = QtImport.QTableWidgetItem(str(position))
                beam_pos_x_column_item = QtImport.QTableWidgetItem(str(position_dict_elem['pos_x']))
                beam_pos_y_column_item = QtImport.QTableWidgetItem(str(position_dict_elem['pos_y']))
                cal_x_item = QtImport.QTableWidgetItem(str(position_dict_elem['cal_x']))
                cal_y_item = QtImport.QTableWidgetItem(str(position_dict_elem['cal_y']))
                light_item = QtImport.QTableWidgetItem(str(position_dict_elem['light']))

                self.ui_widgets_manager.configuration_table.setItem(i, 0, zoom_position_item)
                self.ui_widgets_manager.configuration_table.setItem(i, 1, beam_pos_x_column_item)
                self.ui_widgets_manager.configuration_table.setItem(i, 2, beam_pos_y_column_item)
                self.ui_widgets_manager.configuration_table.setItem(i, 3, cal_x_item)
                self.ui_widgets_manager.configuration_table.setItem(i, 4, cal_y_item)
                self.ui_widgets_manager.configuration_table.setItem(i, 5, light_item)

            self.ui_widgets_manager.configuration_table.itemChanged.connect(
                self.configuration_table_item_changed
            )

        self.ui_widgets_manager.configuration_table.horizontalHeader().setSectionResizeMode(
            QtImport.QHeaderView.ResizeToContents
        )
                
    def init_interface(self):
        """
        Fill table and combobox and make them functional
        """
        self.fill_config_table()
        self.fill_op_modes_list()
        self.load_sessions()
        self.display_data_policy()

    def load_sessions(self):
        """
        Load list of sessions and populate combobox
        """
        self.bliss_session_list = get_sessions_list()
        self.ui_widgets_manager.bliss_session_combo_box.clear()

        for session in self.bliss_session_list:
            self.ui_widgets_manager.bliss_session_combo_box.addItem(
                session
            )

        print(f"ID13CONGI : load_sessions {self.bliss_session_list}")

    def display_data_policy(self, index=0):
        """
        Display data policy of selected session in combobox
        """
        
        if index > -1:
            new_session = self.bliss_session_list[index]
            session_info_string = f"Error loading Bliss session {new_session} configuration"
            print(f"ID13CONGI : display_data_policy new_session {new_session}")
            session = self.bliss_config.get(new_session)
            
            try:
                session.setup()
                session_info_string = session.scan_saving.__info__()
            except RuntimeError:
                logging.getLogger("HWR").error("Exception on Bliss session setup")    

            

            self.ui_widgets_manager.data_policy_label.setText(
                session_info_string
            )
    # def get_zoom_index(self, position_to_find):
    #     if self.multipos_motor_hwobj is not None:
    #         positions = self.multipos_motor_hwobj.get_positions_names_list()
    #         for i, position in enumerate(positions):
    #             if position_to_find == position:
    #                 return(i)
    #         return(-1)

    # def zoom_changed(self, name):
    #     if name is None:
    #         logging.getLogger("HWR").error("Multiple Position motor in no_position state")
    #         return
    #     if self.multipos_motor_hwobj is not None:
    #         self.current_zoom_pos_name = name # self.multipos_motor_hwobj.get_value()
    #         self.current_zoom_idx = self.get_zoom_index(name)
    #         print(f"################ cameraBeamBrick zoom_changed current_zoom_pos_name : {self.current_zoom_pos_name} + current_zoom_idx : {self.current_zoom_idx}")        
    #         if self.current_zoom_idx != -1:
    #             self.current_beam_position = self.beam_position_dict[name]
    #             print(f"################ cameraBeamBrick zoom_changed beampos : {self.current_beam_position} + zoom pos : {self.current_zoom_pos_name}")
    #             if self.ui_widgets_manager.configuration_table.itemAt(self.current_zoom_idx, 1):
    #                 self.ui_widgets_manager.configuration_table.item(self.current_zoom_idx, 1).setText(str(int(self.current_beam_position[0])))
    #                 self.ui_widgets_manager.configuration_table.item(self.current_zoom_idx, 2).setText(str(int(self.current_beam_position[1])))
    #             else:
    #                 print(f"################ cameraBeamBrick zoom_changed TABLE NOT INITIALIZED")
                
    def beam_position_changed(self,beam_x_y):
        """
            beam_x_y (tuple): Position (x, y) [pixel]
        """
        #update current_zoom_idx
        self.current_zoom_pos_name = self.multipos_motor_hwobj.get_value()
        conf_table = self.ui_widgets_manager.configuration_table

        self.current_zoom_idx = -1
        for index in range (conf_table.rowCount()):
            if self.current_zoom_pos_name == conf_table.item(index, 0).text():
                self.current_zoom_idx = index

        if self.current_zoom_idx == -1:
            print(f"################ cameraBeamBrick beam_position_changed ERROR!!! ZOOM POSITION NAME NOT IDENTIFIED!!!")
            return
        
        print(f"################ cameraBeamBrick beam_position_changed beampos : {beam_x_y} + zoom pos : {self.current_zoom_pos_name} - {index}")
        self.current_beam_position = beam_x_y
        
        self.ui_widgets_manager.configuration_table.item(self.current_zoom_idx, 1).setText(str(int(beam_x_y[0])))
        self.ui_widgets_manager.configuration_table.item(self.current_zoom_idx, 2).setText(str(int(beam_x_y[1])))

        self.zoom_positions_dict[self.current_zoom_pos_name]["pos_x"] = self.current_beam_position[0]
        self.zoom_positions_dict[self.current_zoom_pos_name]["pos_y"] = self.current_beam_position[1]

        self.graphic_data_edited.emit(self.zoom_positions_dict)
   
    def save_op_mode_list(self):
        """
        Save data to xml file
        Clean cell background
        """
        xml_file_tree = cElementTree.parse(self.multipos_file_xml_path)
        xml_tree = xml_file_tree.getroot()
                
        xml_tree.find("operational_modes").text = str(self.list_of_operational_modes)

        xml_file_tree.write(self.multipos_file_xml_path)

        self.operation_modes_saved.emit()
    
    def add_op_mode_to_list(self):
        """
        add lable to list
        and to self.list_of_operational_modes
        Data not saved yet
        """
        new_label = self.ui_widgets_manager.new_label_edit.text()
        new_label = new_label.replace(" ", "")

        if not new_label:
            return
        # check if label already exist
        if new_label not in self.list_of_operational_modes:
            self.list_of_operational_modes.append(new_label)
            self.ui_widgets_manager.label_list.addItem(new_label)
            #select newly added item
            self.ui_widgets_manager.label_list.setCurrentRow(
                self.ui_widgets_manager.label_list.count() - 1
            )
            self.operation_modes_edited.emit(self.list_of_operational_modes)
        
    def delete_op_mode_from_list(self):
        """
        delete lable from list
        detele from self.list_of_operational_modes
        changes not saved yet
        """
        label_to_delete = self.ui_widgets_manager.new_label_edit.text()
        label_to_delete = label_to_delete.replace(" ", "")

        if not label_to_delete:
            return

        if label_to_delete not in self.list_of_operational_modes:
            return
        else:
            index = self.list_of_operational_modes.index(label_to_delete)
            self.ui_widgets_manager.label_list.takeItem(index)
            self.list_of_operational_modes.remove(label_to_delete)
            #select first item
            if self.list_of_operational_modes:
                self.ui_widgets_manager.label_list.setCurrentRow(0)
            self.operation_modes_edited.emit(self.list_of_operational_modes)

    def label_list_selection_changed(self, selected_row):
        
        if selected_row != -1:
            selected_item = self.ui_widgets_manager.label_list.item(selected_row)
            self.ui_widgets_manager.new_label_edit.setText(
                selected_item.text()
            )

    def save_table_changes(self):
        """
        Save data to xml file
        Clean cell background
        """
        table = self.ui_widgets_manager.configuration_table

        #open xml file
        xml_file_tree = cElementTree.parse(self.multipos_file_xml_path)

        xml_tree = xml_file_tree.getroot()
        positions = xml_tree.find("positions")
        
        pos_list = positions.findall("position")
        # pdb.set_trace()

        for index, pos in enumerate(pos_list):
            if pos.find('beamx') is not None:
                beamx = self.validate_cell_value(table.item(index, 1).text())
                pos.find('beamx').text = str(beamx)
            if pos.find('beamy') is not None:
                beamy = self.validate_cell_value(table.item(index, 2).text())
                pos.find('beamy').text = str(beamy)
            if pos.find('resox') is not None:
                resox = self.validate_cell_value(table.item(index, 3).text())
                pos.find('resox').text = str(resox * 1e-9)
            if pos.find('resoy') is not None:
                resoy = self.validate_cell_value(table.item(index, 4).text())
                pos.find('resoy').text = str(resoy * 1e-9)
            if pos.find('light') is not None:
                light = self.validate_cell_value(table.item(index, 5).text())
                pos.find('light').text = str(light)
    
        xml_file_tree.write(self.multipos_file_xml_path)

        table.itemChanged.disconnect(
                self.configuration_table_item_changed
            )

        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                table.item(row, col).setData(QtImport.Qt.BackgroundRole, None)
        
        table.itemChanged.connect(
                self.configuration_table_item_changed
            )

        self.graphic_data_saved.emit()
    
    def validate_cell_value(self, input_val):
        """
        return value adapted according to input
        """
        try:
            output = int(input_val)
        except ValueError:
            output = 1

        return output
               
    def cancel_table_changes(self):
        """
        cancel any change in config table.
        reload data from last saved version of xml file
        """
        
        self.load_zoom_positions_dict()
        self.fill_config_table()
    
    def clear_table(self):
        """
        clean table of contents. keep headers
        """
        #table = self.ui_widgets_manager.findChild(QtI
        # mport.QTableWidget, "aligment_table")
        self.ui_widgets_manager.configuration_table.clearContents()        