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
TODO: DELETE THIS BRICK: see ESRFID13ExportDataBrick
ESRF Data Export Brick

[Description]

This brick:

1) displays a list of mutual exclusive checkboxes that especify
the 'operational mode' of the experiment.
The list of the tags of the checkboxes is read from and xml file
( at origin, called multiple-positions )

This file can be edited in any text edit application or even on the
application itself with the ESRFID13ConfigurationTabBrick

2) exports data through json files created throught GUI application manipulation.
Three buttons are available:
    Start : creates Json file and fixes the start_time timestamp on the json file. 
    Actions on the GUI application will be recorded on the file from this momment
    Apply : experiment data ( motor positions, points of interest, calibration data, beamline positions...)
    will be written on the json file
    Cancel : 'close' Json file, nothing will be recorded untill 'Start' is pressed again.


TODO:
Json file schema


[Properties]

xml file

[Signals]

[Slots]

reload_operation_mode_list : update the list of tags/checkboxes

TODO : delete this
data_base_path_changed(str) - slot to be connected to ESRFID13ConfigurationTabBrick
                             data_path_base_changed signal

data_policy_changed(str) - slot to be connected to ESRFID13ConfigurationTabBrick
                             data_policy_changed signal


[Comments]

"""

import sys
import math
import logging
import os
import json
import time
import datetime
from datetime import date

import copy
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

class ESRFDataExportBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # variables -----------------------------------------------------------

        self.list_of_operational_modes = []
        self.multipos_file_path = None
        self.action_group = None
        self.data_base_path = None
        self.json_file_index = 2
        self.json_file_name = 'id13ExportData' + "_" + str(self.json_file_index) + ".json"

        # Hardware objects ----------------------------------------------------
        
        # Internal values -----------------------------------------------------
        
        # Properties ----------------------------------------------------------
        self.add_property("configfile", "string", "")
        
        # Signals ------------------------------------------------------------
        
        # Slots ---------------------------------------------------------------
        self.define_slot("reload_operation_mode_list", ())
        self.define_slot("data_base_path_changed", ())
        self.define_slot("data_policy_changed", ())
                
        # Graphic elements ----------------------------------------------------
        # self.main_groupbox = QtImport.QGroupBox("Data export", self)
        self.ui_widgets_manager = QtImport.load_ui_file("data_export_widget.ui")

        # Size policy --------------------------------
        self.ui_widgets_manager.operation_mode_groupbox.setSizePolicy(
            QtImport.QSizePolicy.Minimum,
            QtImport.QSizePolicy.Minimum,
        )

        # Layout --------------------------------------------------------------
        # _groupbox_vlayout = QtImport.QVBoxLayout(self)
        # _groupbox_vlayout.addWidget(self.ui_widgets_manager)
        # _groupbox_vlayout.setSpacing(0)
        # _groupbox_vlayout.setContentsMargins(0, 0, 0, 0)
        # self.main_groupbox.setLayout(_groupbox_vlayout)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.ui_widgets_manager)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(_main_vlayout)

        # Qt signal/slot connections ------------------------------------------
       
        self.ui_widgets_manager.start_button.clicked.connect(
            self.start_data_export
        )

        self.ui_widgets_manager.apply_button.clicked.connect(
            self.apply_data_export
        )

        self.ui_widgets_manager.cancel_button.clicked.connect(
            self.cancel_data_export
        )

        # Other hardware object connections --------------------------
        
        self.init_interface()

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "configfile":
            if new_value.startswith("/"):
                    new_value = new_value[1:]

            self.multipos_file_path = os.path.join(
                HWR.getHardwareRepositoryConfigPath(),
                new_value + ".xml")

            self.load_list_of_operational_modes()
            self.init_interface()

        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def init_interface(self):
        """
        Fill mutual exclusive list of checkboxes
        """

        print(f"init_interface@@@@@@@ self.list_of_operational_modes {self.list_of_operational_modes}")
        if self.list_of_operational_modes:
            # delete checkboxes in operation_mode_groupbox
            groupbox = self.ui_widgets_manager.operation_mode_groupbox
            groupbox_layout = QtImport.QVBoxLayout()
            for widget in groupbox.findChildren(QtImport.QRadioButton, "", QtImport.Qt.FindDirectChildrenOnly):
                widget.deleteLater()
            
            if self.action_group:
                self.action_group.deleteLater()
            
            self.action_group = QtImport.QButtonGroup(groupbox)
            # create new checkboxes
            for tag in self.list_of_operational_modes:
                checkbox = QtImport.QRadioButton(tag, groupbox)
                groupbox_layout.addWidget(checkbox)
                self.action_group.addButton(checkbox)
            
            groupbox.setLayout(groupbox_layout)

            self.ui_widgets_manager.data_path_base_label.setText(
                self.data_base_path
            )
            self.ui_widgets_manager.file_index_label.setText(
                str(self.json_file_index)
            )

    def create_export_data(self):
        self.data = {}

        # more precission
        # time_in_seconds = time.time()
        # dt = datetime.datetime.fromtimestamp(time_in_seconds)
        # formated_time_in_msc = dt.strftime('%Y-%m-%d %H:%M:%S')
        # formated_time_in_msc += '.' + str(time_in_seconds % 1)

        # more simple
        now = datetime.datetime.now()
        self.data['timestamp'] = str(now)
    
    def data_policy_changed(self, data_policy_full_info):
        """
        param : data_policy_full_info
            data policy full info as given by bliss' SCAN_SAVING.__info__()
        """

        # search for sample info in data_policy_full_info

        #split string with \n
        info_list = data_policy_full_info.split('\n')
        print(info_list)

        for info in info_list:
            if ".base_path" in info:
                print(info)
                info_split = info.split('=')
                self.ui_widgets_manager.sample_name_tbox.setText(info_split[1])


    def data_base_path_changed(self, data_base_path):

        self.data_base_path = data_base_path
        self.ui_widgets_manager.data_path_base_label.setText(
            self.data_base_path
        )

    def reload_operation_mode_list(self):
        pass

    def start_data_export(self):
        """

        """
    def apply_data_export(self):
        """
        
        """
    def cancel_data_export(self):
        """
        
        """
    
    def load_list_of_operational_modes(self):
        """
        Parse xml file and load list of operational modes :

        'tag0', 'tag1', ...
        """
        xml_file_tree = cElementTree.parse(self.multipos_file_path)

        xml_tree = xml_file_tree.getroot()
        mode_list = []
        if xml_tree.find("operational_modes") is not None:
            mode_list = xml_tree.find("operational_modes").text
            print(f"DATAEXPORT@@@@@@@@@@@@@@@@ : mode_list : {mode_list} - {type(mode_list)} ")
            self.list_of_operational_modes = eval(mode_list)
        else:
            print(f"DATAEXPORT@@@@@@@@@@@@@@@@ : xml_tree EMPTY")          
